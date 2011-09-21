class DictObject:
    def __init__(self, **entries): 
        self.__dict__.update(entries)

    def __eq__(self, other):
          return self.__dict__ == other.__dict__
