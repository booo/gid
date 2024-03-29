import os
import re

from dulwich.repo import Repo
from dulwich.walk import Walker

from objects.commit import GitCommit
from objects.tree import GitTree
from objects.blob import GitBlob

class GitRepository:
    "Representation of a git repository"

    def __init__(self, path, init = False):
        if init :
          os.makedirs(path)
          repo = Repo.init_bare(path)
        else:
          repo = Repo(path)


        self._repo    = repo
        self.path     = path
        self.branches = self._getBranches() 

        try:
            head = repo.head()
            commitLast = repo.commit(head)
            
            self.head     = {
                'sha'    : head,
                'tree'   : commitLast.tree
            }
        except KeyError:
            self.head = None


    def _getBranches(self):
        """Gets all branches of a repo"""
        filterForBranch = lambda s : "refs/heads" in s
        refs = self._repo.get_refs()

        return [ 
            { 
              'path'  : k.split('/')[-1],
              'sha'   : refs[k] 
            } for k in refs.keys() if filterForBranch(k) 
          ]


    def getCommit(self, sha):
        return GitCommit(self._repo, sha).toDict()


    def getCommits(self, amount = None, start = None, branch = None):
        commits = []

        if start:
          amount += start

        try:
            sha = [ branch if branch else self._repo.head() ]
            walker = Walker(self._repo.object_store, sha, max_entries = amount)

            if walker is not None:
              commits = [
                          GitCommit(self._repo, entry.commit.id).toDict(True)
                          for entry in walker
                        ]



        except KeyError:
          pass

        return commits[start:]

    def getBlob(self, sha):
        return GitBlob(self._repo.get_blob(sha)).toDict()

    def getTree(self, sha, recursively = False):
        return GitTree(self._repo, self._repo.tree(sha)).toDict(recursively)

    def toDict(self):
        return {
            'path'      : self.path,
            'head'      : self.head,
            'branches'  : self.branches
          }
