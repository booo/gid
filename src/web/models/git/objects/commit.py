from datetime import datetime

class GitCommit:

    def __init__(self, commit):
        self.commit = commit

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
        short = {
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
          return short

        else:
          return short
