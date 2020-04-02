class JsonWrapper:
    def __init__(self, data):
        self.data = data

    def get(self, key):
        if(key in self.data):
            return(self.data[key])
