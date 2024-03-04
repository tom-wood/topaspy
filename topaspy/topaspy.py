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
        self.uncommented_string = self.remove_comments(raw_string)
    
    def remove_comments(self, raw_string):
        lines = raw_string.split('\n')
        new_lines = []
        block_comment = False
        for line in lines:
            new_line = self.remove_line_comment(line)
            #get block comments
            while any(['/*' in new_line, '*/' in new_line]):
                if block_comment:
                    if '*/' in new_line:
                        new_line = new_line[new_line.index('*/') + 2:]
                        print(new_line)
                        block_comment = False
                else:
                    if '/*' in new_line:
                        ni = new_line.index('/*')
                        if ni:
                            new_lines.append(new_line[:ni])
                        new_line = new_line[ni + 2:]
                        block_comment = True
            if not block_comment:
                if len(new_line):
                    new_lines.append(new_line)
        return new_lines

    @staticmethod
    def remove_line_comment(line):
        if "'" in line:
            new_line = line[:line.index("'")]
            return new_line
        else:
            return line