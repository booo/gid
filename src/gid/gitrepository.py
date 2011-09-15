import os
import re

from dulwich.repo import Repo 

class GitRepository:

    folder = "data/git"

    @staticmethod
    def _sanitize(value):
      return unicode(re.sub('[^\w-]', '', value).strip().lower())

    @staticmethod
    def _path(userName, repoName):
        return os.path.sep.join([ os.path.dirname(__file__), "..", "..",\
                                  GitRepository.folder, userName, \
                                  GitRepository._sanitize(repoName)
                                ])


    @staticmethod
    def _get(repoName, userName):
        path = GitRepository._path(userName, repoName)
        return Repo(path)


    @staticmethod
    def create(repoName, userName):
        path = GitRepository._path(userName, repoName)
        os.makedirs(path)
        Repo.init(path)

    @staticmethod
    def delete(repoName, userName):
        path = GitRepository._path(userName, repoName)
        if os.path.isdir(path + os.path.sep + ".git"):
          shutil.rmtree(path)

    @staticmethod
    def show(repoName, userName):
        repo = GitRepository._get(repoName, userName)
        refs = []
        for ref in repo.refs.allkeys():
          refs.append(ref)

        repoContent = {
          "name": repoName,
          "refs": refs,
        }
        
        return repoContent

