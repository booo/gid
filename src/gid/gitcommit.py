from gid.gitrepository import GitRepository
from dulwich.walk import Walker

class GitCommit:

    @staticmethod
    def list(repoName, userName):
      repo = GitRepository._get(repoName, userName) 

      commits = []
      try:
        walker = Walker(repo.object_store, [repo.head()])
        for entry in walker:
          changes = []
          for change in entry.changes():
            changes.append({
              "type" : change.type,
              "path" : {
                "old" : change.old.path,
                "new" : change.new.path
               }
            })

          commit = {
            "sha" : entry.commit.id,
            "message" : entry.commit.message,
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
