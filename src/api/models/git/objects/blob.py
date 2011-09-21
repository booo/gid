from tree import entryType

class GitBlob:
  
  def __init__(self, blob):
      self.sha      = blob.id,
      self.content  = blob.data,
      self.length   = blob.raw_length()
      self.blobType = blob.get_type()


  def toDict(self):
    return {
        "sha"     : self.sha,
        "content" : self.content,
        "length"  : self.length,
        "type"    : entryType[self.blobType]
      }
