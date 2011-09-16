from gid.gitrepository import GitRepository
from dulwich.walk import Walker
from datetime import datetime

class GitCommit:

    @staticmethod
    def _toDate(timestamp):
          return datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def list(repoName, userName):
      repo = GitRepository._get(repoName, userName) 

      commits = []
      try:
        walker = Walker(repo.object_store, [repo.head()])
        for entry in walker:
          changes = []
          for change in entry.changes():
            if hasattr(change, 'type'):
              changes.append({
                "type" : change.type,
                "path" : {
                  "old" : change.old.path,
                  "new" : change.new.path
                 }
              })


          commit = {
            "id" : entry.commit.id,
            "message" : entry.commit.message,
            "committer" : {
              "name": entry.commit.committer,
              "date": GitCommit._toDate(entry.commit.commit_time)
            },
            "author" : {
              "name": entry.commit.author,
              "date": GitCommit._toDate(entry.commit.author_time)
            },
            "changes" : changes
          }

          commits.append(commit)
          

      except KeyError:
        pass
      
      return commits

    @staticmethod
    def show(repoName, userName, sha):
      repo = GitRepository._get(repoName, userName) 
      commit = repo.commit(sha)

      def traverse(items):
          entries = []
          for item in items:
              if repo.get_object(item.sha).get_type() == 3:
                  entry = {\
                    'path' : item.path,\
                    'sha' : item.sha,\
                    'childs': None\
                  }
                  entries.append(entry)
              else:
                  entry = {\
                    'path' : item.path,\
                    'sha' : item.sha,\
                    'childs': traverse(repo.tree(item.sha).iteritems())\
                  }
                  entries.append(entry)
          return entries

      tree = traverse(repo.tree(commit.tree).iteritems())

      return {
        "sha" : commit.id,
        "author": commit.author,
        "committer": commit.committer,
        "commit_time": commit.commit_time,
        "message" : commit.message,
        "repository" : repoName,
        "tree": tree
      }
