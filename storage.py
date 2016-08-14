import json


def transactional(func):
    def decorator(self, *args, **kwargs):
        self.from_storage()
        result = func(self, *args, **kwargs)
        self.to_storage()
        return result

    return decorator


class Storage:
    def __init__(self, file_name):
        self.file_name = file_name
        self.storage = []
        self.to_storage()

    def getRaw(self):
        with open(self.file_name, 'r+') as f:
            content = f.read()
            return content

    @transactional
    def put(self, obj):
        self.storage.append(obj)

    @transactional
    def getAll(self):
        return self.storage

    @transactional
    def erase(self):
        self.storage = []

    def from_storage(self):
        with open(self.file_name, 'r+') as f:
            content = f.read()
            self.storage = json.loads(content)

    def to_storage(self):
        with open(self.file_name, 'w+') as f:
            content = json.dumps(self.storage)
            f.write(content)
