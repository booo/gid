entryType = [
  "unknown", "unknown","folder","file"
]

class GitTree:
  
  def __init__(self, repo, tree):
      self.repo  = repo
      self.tree  = tree

  def _entryAsDict(self, entry):
      return {
          'path'  : entry.path,
          'type'  : entryType[self.repo.get_object(entry.sha).get_type()],
          'sha'   : entry.sha 
        }


  def _traverse(self, sha):
      print "sha" + str(sha)
      iterator = self.repo.tree(sha).iteritems()

      return [
          self._entryAsDict(item) for item in iterator
        ]


  def _traverseRecursively(self, sha):
      treeEntries = []

      entries = self.repo.tree(sha).iteritems()
      for entry in entries:
          item = self._entryAsDict(entry)

          if item['type'] == 'folder':
              item['childs'] = self._traverseRecursively(item['sha'])

          treeEntries.append(item)

      return treeEntries


  def toDict(self, recursively = False):
      if recursively:
          return self._traverseRecursively(self.tree.id)

      return self._traverse(self.tree.id)
