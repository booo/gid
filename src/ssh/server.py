#!/usr/bin/env python
import yaml
import sys, re, os, shlex

from twisted.cred import portal, checkers
from twisted.conch import error, avatar
from twisted.conch.checkers import SSHPublicKeyDatabase
from twisted.conch.ssh import factory, userauth, connection, keys, session, channel
from twisted.internet import reactor, protocol, defer
from twisted.python import log, components

from api.models.user import User
from api.models.repository import Repository
from api.models.activity import Activity
from api import db

log.startLogging(sys.stderr)

stream = file('config/main.yaml', 'r')
config = yaml.load(stream)

publicKey = config['SSH_PUBLIC_KEY']
privateKey = config['SSH_PRIVATE_KEY']

class PubKeyChecker(SSHPublicKeyDatabase):

    def checkKey(self, credentials):
        user = User.query.filter_by(
            keyBlob = credentials.blob
        ).first()

        return user != None

# Work around weird bug in Conch.
class PatchedSSHSession(session.SSHSession):

    def loseConnection(self):
        if getattr(self.client, 'transport', None) is not None:
            self.client.transport.loseConnection()
        channel.SSHChannel.loseConnection(self)

class GitUser(avatar.ConchUser):
    def __init__(self, name):
        avatar.ConchUser.__init__(self)

        self.name = name

        self.user =  User.query.filter_by(
              username = name
          ).first()


        print self.user

        self.channelLookup['session'] = PatchedSSHSession


    @staticmethod
    def _getUserAndRepo(name):
        username = name.split('/')[0]
        reponame = name.split('/')[1]

        return username, reponame


    def can(self, perm, name):
        """ Checks for permission to a repository """

        username, reponame = self._getUserAndRepo(name)

        owner = User.query.filter_by(username=username).first()
        repo = Repository.query.filter_by(
                  name = reponame,
                  owner = owner
               ).first()

        if owner.username == username:
          return True

        elif perm == 'read' and not repo.private:
          return True

        else:
          return False


    def addActivity(self, command, name):
        """ Adds push activity into the database """
        
        username, reponame = self._getUserAndRepo(name)

        owner = User.query.filter_by(username=username).first()
        repo = Repository.query.filter_by(
                  name = reponame,
                  owner = owner
               ).first()

        if "git-receive-pack" in command:
            activityType = "push"
            activity = Activity(activityType, repo)
            owner.activities.append(activity)

            db.session.add(activity)
            db.session.commit()


class GitRealm:
    def requestAvatar(self, avatarId, mind, *interfaces):
        user = GitUser(avatarId)
        return interfaces[0], user, lambda: None

class GitChannel:

    def __init__(self, avatar):
        self.avatar = avatar

    def getPty(self, term, windowSize, attrs):
        """
        Just accept PTY requests to make the client happy.
        Not necessary for git though.
        """
        pass

    def openShell(self, proto):
        """
        When the client requests a shell, we tell him that he won't get one
        and close the connection.
        """
        proto.write("No shell here. Go away.\r\n")
        proto.loseConnection()
        return True

    def execCommand(self, proto, raw_command):
        """ An exec request will be processed by the GitCommand class. """
        GitCommand(self.avatar, proto, raw_command).run()

    def eofReceived(self):
        pass

    def closed(self):
        pass

class GitCommand:
    """ Maps git commands to the permission they require. """

    command_permissions = {
            'git-upload-pack':    'read',
            'git-upload-archive': 'read',
            'git-receive-pack':   'write'
    }

    def __init__(self, avatar, protocol, raw_command):
        self.avatar            = avatar
        self.protocol        = protocol

        (self.command, self.repository) = self.processCommand(raw_command)

    def processCommand(self, raw_command):
        """ Parses a full git command line into its command and its repository. """
        argv = shlex.split(raw_command)

        cmd_name    = argv[0]

        # Grab the requested path and remove leading slashes.
        repo_name = re.sub('^/+', '', argv[-1])

        return (cmd_name, repo_name)

    def run(self):
        """ Entry point for this handler. """
        if not self.validate():  return True
        if not self.authorize(): return True

        # Build absolute path.
        path = os.path.join(os.getcwd(), "data", "git", self.repository)


        print "Path: "+path

        # Reconstruct the command.
        command = ' '.join([self.command, "'%s'" % path])

        shell = '/usr/bin/git-shell'

        # Actually fire the whole thing.
        reactor.spawnProcess(self.protocol, shell, [shell, '-c', command])

        # Add activity entry
        self.avatar.addActivity(self.command, self.repository)

    def validate(self):
        """ Validates this request before actually executing anything. """
        # Check repository format.
        if not re.match('^\w+/\w+', self.repository):
            return self.error("ERROR: Invalid repository name.\n")

        return True

    def authorize(self):
        """ Makes sure that the current user has permission to execute. """
        permission = self.command_permissions[self.command]

        if permission and self.avatar.can(permission, self.repository):
            return True
        else:
            return self.error("ERROR: Unknown or restricted repository.\n")

    def error(self, message):
        """ Writes an error to the client and closes the connection. """
        self.protocol.errReceived(message)
        self.protocol.loseConnection()
        return False

class GitFactory(factory.SSHFactory):
    publicKeys = {
        'ssh-rsa': keys.Key.fromString(data=publicKey)
    }

    privateKeys = {
        'ssh-rsa': keys.Key.fromString(data=privateKey)
    }

    services = {
        'ssh-userauth':   userauth.SSHUserAuthServer,
        'ssh-connection': connection.SSHConnection
    }

components.registerAdapter(GitChannel, GitUser, session.ISession)

portal = portal.Portal(GitRealm())

# Add pubkey auth
portal.registerChecker(PubKeyChecker())

GitFactory.portal = portal

def run(port = 5022):
    reactor.listenTCP(port, GitFactory())
    reactor.run()
