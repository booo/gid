#!/usr/bin/env python

from twisted.cred import portal, checkers
from twisted.conch import error, avatar
from twisted.conch.checkers import SSHPublicKeyDatabase
from twisted.conch.ssh import factory, userauth, connection, keys, session, channel
from twisted.internet import reactor, protocol, defer
from twisted.python import log, components
import sys, re, os, shlex
from web.models.user import User

log.startLogging(sys.stderr)

publicKey = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAGEArzJx8OYOnJmzf4tfBEvLi8DVPrJ3/c9k2I/Az64fxjHf9imyRJbixtQhlH9lfNjUIx+4LmrJH5QNRsFporcHDKOTwTTYLh5KmRpslkYHRivcJSkbh/C+BR3utDS555mV'

privateKey = """-----BEGIN RSA PRIVATE KEY-----
MIIByAIBAAJhAK8ycfDmDpyZs3+LXwRLy4vA1T6yd/3PZNiPwM+uH8Yx3/YpskSW
4sbUIZR/ZXzY1CMfuC5qyR+UDUbBaaK3Bwyjk8E02C4eSpkabJZGB0Yr3CUpG4fw
vgUd7rQ0ueeZlQIBIwJgbh+1VZfr7WftK5lu7MHtqE1S1vPWZQYE3+VUn8yJADyb
Z4fsZaCrzW9lkIqXkE3GIY+ojdhZhkO1gbG0118sIgphwSWKRxK0mvh6ERxKqIt1
xJEJO74EykXZV4oNJ8sjAjEA3J9r2ZghVhGN6V8DnQrTk24Td0E8hU8AcP0FVP+8
PQm/g/aXf2QQkQT+omdHVEJrAjEAy0pL0EBH6EVS98evDCBtQw22OZT52qXlAwZ2
gyTriKFVoqjeEjt3SZKKqXHSApP/AjBLpF99zcJJZRq2abgYlf9lv1chkrWqDHUu
DZttmYJeEfiFBBavVYIF1dOlZT0G8jMCMBc7sOSZodFnAiryP+Qg9otSBjJ3bQML
pSTqy7c3a2AScC/YyOwkDaICHnnD3XyjMwIxALRzl0tQEKMXs6hH8ToUdlLROCrP
EhQ0wahUTCk1gKA4uPD6TMTChavbh4K63OvbKg==
-----END RSA PRIVATE KEY-----"""

class PubKeyChecker(SSHPublicKeyDatabase):

  def checkKey(self, credentials):
    return True
    #return credentials.username == 'user' and keys.Key.fromString(data=publicKey).blob() == credentials.blob

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
    self.channelLookup['session'] = PatchedSSHSession

  """ Checks for permission to a repository """
  def can(self, perm, repo):
    if perm == 'write': return True
    else: return True

class GitRealm:
  def requestAvatar(self, avatarId, mind, *interfaces):
    user = GitUser(avatarId)
    return interfaces[0], user, lambda: None

class GitChannel:

  def __init__(self, avatar):
    self.avatar = avatar

  """
  Just accept PTY requests to make the client happy.
  Not necessary for git though.
  """
  def getPty(self, term, windowSize, attrs):
    pass

  """
  When the client requests a shell, we tell him that he won't get one
  and close the connection.
  """
  def openShell(self, proto):
    proto.write("No shell here. Go away.\r\n")
    proto.loseConnection()
    return True

  """
  An exec request will be processed by the GitCommand class.
  """
  def execCommand(self, proto, raw_command):
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
    self.avatar      = avatar
    self.protocol    = protocol

    (self.command, self.repository) = self.processCommand(raw_command)

  """ Parses a full git command line into its command and its repository. """
  def processCommand(self, raw_command):
    argv = shlex.split(raw_command)

    cmd_name  = argv[0]

    # Grab the requested path and remove leading slashes.
    repo_name = re.sub('^/+', '', argv[-1])

    return (cmd_name, repo_name)

  """ Entry point for this handler. """
  def run(self):
    if not self.validate():  return True
    if not self.authorize(): return True

    # Build absolute path.
    path = os.path.join(os.getcwd(), self.repository)

    # Reconstruct the command.
    command = ' '.join([self.command, "'%s'" % path])

    shell = '/usr/bin/git-shell'

    # Actually fire the whole thing.
    reactor.spawnProcess(self.protocol, shell, [shell, '-c', command])

  """ Validates this request before actually executing anything. """
  def validate(self):
    # Check repository format.
    if not re.match('^\w+/\w+', self.repository):
      return self.error("ERROR: Invalid repository name.\n")

    return True

  """ Makes sure that the current user has permission to execute. """
  def authorize(self):
    permission = self.command_permissions[self.command]

    if permission and self.avatar.can(permission, self.repository):
      return True
    else:
      return self.error("ERROR: Unknown or restricted repository.\n")

  """ Writes an error to the client and closes the connection. """
  def error(self, message):
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

if __name__ == '__main__':
    reactor.listenTCP(5022, GitFactory())
    reactor.run()
