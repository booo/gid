from dulwich.patch import write_tree_diff
import sys

from datetime import datetime

class GitCommit:

    def __init__(self, repo, sha):
        self._repo = repo
        self.commit = repo.commit(sha)

    @staticmethod
    def _toDate(timestamp, timezone):
          return datetime.fromtimestamp(int(timestamp)).\
                    strftime('%Y-%m-%d %H:%M:%S') + '+' + str(timezone)
    
    def toDict(self, short = False):
        authorDate = GitCommit._toDate(
                        self.commit.author_time,
                        self.commit.author_timezone
                     )

        commitDate = GitCommit._toDate(
                        self.commit.commit_time,
                        self.commit.commit_timezone
                     )
        data = {
            "sha"         : self.commit.id,
            "message"     : self.commit.message,
            "tree"        : self.commit.tree,
            "parents"     : self.commit.parents,
            "author"      : {
                "name"      : self.commit.author,
                "date"      : authorDate
              },
            "committer"   : {
                "name"      : self.commit.committer,
                "date"      : commitDate 
              },
          }

        if short:
          return data

        import StringIO
        changes = StringIO.StringIO()
        write_tree_diff(
          changes,
          self._repo.object_store,
          self.commit.tree,
          self._repo.commit(self.commit.parents[0]).tree
        )
        data['changes'] = changes.getvalue()
        changes.close()

        return data
