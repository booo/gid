from gid.gitrepository import GitRepository

class GitBlob:

  @staticmethod
  def show(repoName, userName, sha):
      repo = GitRepository._get(repoName, userName) 
      obj =  repo.get_object(sha)

      data = {
        "content":  obj.data,
        "rawLength": obj.raw_length(),
        "type": obj.get_type(),
        "sha": sha
      }

      return data
