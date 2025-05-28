class History:

    def __init__(self):
        self._items = []

    def add(self, keyword):
        if keyword not in self._items:
            self._items.append(keyword)

    def clear(self):
        self._items.clear()

    def get_all(self):
        return self._items.copy()