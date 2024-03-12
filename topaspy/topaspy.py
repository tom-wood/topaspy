class Input:
    def __init__(self, fname):
        self._fname = fname
        self.xdds = []
        self.reset_gof_params()
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
    
    def parse_file(self):
        gof = False
        xdd = False
        in_xdd = False
        xdd_count = 0
        for line in self.uncommented_string:
            for s in line.split():
                if gof:
                    self.gof_params[gof_kw] = float(s)
                    gof = False
                    continue
                if s in self.gof_params:
                    gof = True
                    gof_kw = s
                    continue
                if in_xdd:
                    if op:
                        xdd_now.other_props[op_kw] = float(s)
                        op = False
                        continue
                    if s in xdd_now.other_props:
                        op = True
                        op_kw = s
                        continue
                if s == 'xdd':
                    xdd = True
                    xdd_count += 1
                    continue
                if xdd:
                    if '"' in s:
                        #doesn't deal with spaces in filename
                        self.xdds.append(XDD(s.split('"')[1]))
                    else:
                        self.xdds.append(XDD(s))
                    xdd = False
                    in_xdd = True
                    xdd_now = self.xdds[xdd_count - 1]
                    op = False
                    continue

    def reset_gof_params(self):
        self.gof_params = {'r_exp' : 0.,
                           'r_wp' : 0.,
                           'r_p' : 0.,
                           'r_exp_dash' : 0.,
                           'r_wp_dash' : 0.,
                           'r_p_dash' : 0.,
                           'weighted_Durbin_Watson' : 0.,
                           'gof' : 0.,}

class XDD:
    def __init__(self, fname):
        self._fname = fname
        self.strucs = []
        self.other_props = {'start_X' : 0.,
                            'finish_X' : 0.,
                            'x_calculation_step' : 0.,
                            'ymin_on_ymax' : 0.}

#TOPAS Technical reference information
#reserved_params = {'A_star', 'B_star', 'C_star',
#                   'Change', 'D_spacing', 'H', 'K',
#                   'L', 'M', 'Iter', 'Cycle',
#                   'Cycle_Iter', 'Lam', 'Lpa', 'Lpb',
#                   'Lpc', 'Mi', 'Peak_Calculation_Step',
#                   'QR_Removed', 'QR_Num_Times_Consecutively_Small',
#                   'R', 'Ri'}
