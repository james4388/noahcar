class MemoryBus(dict):
    '''
        Extend dict object to put/get multiple key/value pairs at once
    '''
    def __init__(self, *args, **kwargs):
        super(MemoryBus, self).__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        if not isinstance(key, (tuple, list)):
            super(MemoryBus, self).__setitem__(key, value)
        else:
            assert len(key) == len(value)
            for k, v in zip(key, value):
                super(MemoryBus, self).__setitem__(k, v)

    def __getitem__(self, key):
        if isinstance(key, (list, tuple)):
            return [super(MemoryBus, key).__getitem__(k) for k in key]
        return super(MemoryBus, self).__getitem__(key)

    def get(self, keys, default=None):
        if not isinstance(keys, (tuple, list)):
            keys = (keys, )
        return [super(MemoryBus, self).get(k, default) for k in keys]

    def put(self, keys, values):
        self.__setitem__(keys, values)
