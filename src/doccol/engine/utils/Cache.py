
class Cache(object):
    '''Basic in-memory caching implementation'''

    def __init__(self, max_size, close_cb=None):
        self.__max_size = max_size
        self.__close_cb = close_cb
        self.__entries = dict()
        self.__entry_order = list()


    def add(self, key, value):

        # Clean out cache
        while len(self.__entry_order) > self.__max_size - 1:
            self.remove_oldest()

        # Remove key if exists
        if self.has(key):
            self.remove(key)

        # Add entry
        self.__entry_order.append(key)
        self.__entries[key] = value


    def has(self, key):
        return self.__entries.has_key(key)


    def get(self, key):
        return self.__entries[key]


    def remove(self, key):
        if self.has(key):
            del self.__entries[key]
            self.__entry_order.remove(key)


    def remove_oldest(self):
        if len(self.__entry_order) > 0:
            del self.__entries[self.__entry_order.pop(0)]
