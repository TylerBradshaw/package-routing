class GenerateHashMap:
    """
    A basic implementation of a hash map using open addressing.
    """
    def __init__(self, size=16):
        self.map = [None] * size
        self.count = 0

    def __get_hash(self, key):
        return hash(key) % len(self.map)

    def insert(self, key, value):
        i = self.__get_hash(key)
        key_value_pair = [key, value]

        if self.map[i] is None:
            self.map[i] = [key_value_pair]
            self.count += 1
            return True
        else:
            for item in self.map[i]:
                if item[0] == key:
                    item[1] = value
                    return True
            self.map[i].append(key_value_pair)
            self.count += 1
            return True

    def lookup(self, key):
        items = self.map[self.__get_hash(key)]
        if items:
            for item in items:
                if item[0] == key:
                    return item[1]
        return None

    def remove(self, key):
        j = self.__get_hash(key)
        for index, item in enumerate(self.map[j]):
            if item[0] == key:
                self.map[j].pop(index)
                self.count -= 1
                return True
        return False

    # For testing and debugging
    def __str__(self):
        return str(self.map)

    def __contains__(self, key):
        return self.lookup(key) is not None

    def __len__(self):
        return self.count
