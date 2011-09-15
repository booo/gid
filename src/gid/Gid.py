import os
import shutil
import re
import sys
from os import path

from dulwich.repo import Repo
from dulwich.walk import Walker
from dulwich.errors import NotGitRepository

GIT_DIR = path.dirname(path.abspath(__file__)) + os.path.sep + ".." \
                         + os.path.sep + ".." + os.path.sep + "data" \
                         + os.path.sep + "git"

class Gid:
    """Simple git daemon class"""

    prefix_dir = ""

    def __init__(self, prefix = GIT_DIR):
      self.prefix_dir = prefix


    def _sanitize(self, value):
      return unicode(re.sub('[^\w\s-]', '', value).strip().lower())


    def list(self):
      repos = []

      for dir_entry in os.listdir(self.prefix_dir):
        git_dir = self.prefix_dir + os.path.sep +  dir_entry
        print git_dir

        try:
          t = Repo(git_dir)
          repos.append(dir_entry)
        except NotGitRepository:
          pass

      return repos

    def create(self, name):
      repo_name = self._sanitize(name)
      path = self.prefix_dir + os.path.sep + repo_name
      repo = Repo.init(path,  True)
      print "\nCreated Repo: " + repo_name + "\n"

      return repo_name, repo

    def commit(self, repo, sha):
      repo_name = self._sanitize(repo)
      repo = Repo(self.prefix_dir + os.path.sep + repo_name)
      commit = repo.commit(sha)

      def traverse(items):
          entries = []
          for item in items:
              if repo.get_object(item.sha).get_type() == 3:
                  entries.append(item.path)
              else:
                  entry = (item.path, traverse(repo.tree(item.sha).iteritems()))
                  entries.append(entry)
          return entries

      tree = traverse(repo.tree(commit.tree).iteritems())

      return {
        "sha" : commit.id,
        "author": commit.author,
        "committer": commit.committer,
        "commit_time": commit.commit_time,
        "message" : commit.message,
        "repository" : repo_name,
        "tree": tree
      }
     

    def detail(self, name):
      repo_name = self._sanitize(name)
      repo = Repo(self.prefix_dir + os.path.sep + repo_name)
     
      refs = []
      for ref in repo.refs.allkeys():
        refs.append(ref)


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

      repoContent = {
        "name": repo_name,
        "refs": refs,
        "commits": commits
      }
      
      return repoContent

    def delete(self, name):
      repo_name = self._sanitize(name)
      path = self.prefix_dir + os.path.sep + repo_name
      if os.path.isdir(path + os.path.sep + ".git"):
        shutil.rmtree(path)
        print "\nDeleted Repo: " + repo_name + "\n"
