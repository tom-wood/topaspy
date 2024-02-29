class Input:
    def __init__(self, fname):
        self._fname = fname
        self.reload_file()
    
    @property
    def fname(self):
        return self._fname
    
    @fname.setter
    def fname(self, val):
        self._fname = val
        self.reload_file()
    
    def reload_file(self):
        with open(self._fname, 'r') as f:
            self.raw_string = f.read()
        self.parse_raw_string(self.raw_string)
    
    def parse_raw_string(self, raw_string):
        pass