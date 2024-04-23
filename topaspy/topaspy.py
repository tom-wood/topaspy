#TODO
#1. deal with prm
#2. deal with PVs?
#3. method to plot Chebyshevs
#4. Get structures sorted!

class Input:
    """Class to extract and hold data from a TOPAS input file"""
    def __init__(self, fname : str) -> None:
        """
        Args:
            fname (str): filename of input file
        """
        self._fname = fname
        self.xdds = []
        self.macros = dict()
        self.prms = dict()
        self.reset_gof_params()
        self.reload_file()
    
    @property
    def fname(self):
        return self._fname
    
    @fname.setter
    def fname(self, val):
        self._fname = val
        self.reload_file()
    
    def reload_file(self) -> None:
        """Reload input file"""
        with open(self._fname, 'r') as f:
            self.raw_string = f.read()
        self.parse_raw_string(self.raw_string)
    
    def parse_raw_string(self, raw_string : str) -> None:
        """Parse raw string to make sure that comments are removed

        Args:
            raw_string (str): string of input file
        """
        self.uncommented_string = self.remove_comments(raw_string)
    
    def remove_comments(self, raw_string : str) -> list:
        """Remove comments from input file string and split into lines
        
        Args:
            raw_string (str): string of input file
        Returns:
            new_lines (list): list of strings, where each string represents a
            line in the file without the comments (empty lines are ignored)
        """
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
    def remove_line_comment(line : str) -> str:
        """Remove a line comment from a string (one preceded by a ' mark)
        
        Args:
            line (str): string of an input file line
        Returns:
            new_line (str): string of input file line without any comments
        """
        if "'" in line:
            new_line = line[:line.index("'")]
            return new_line
        else:
            return line
    
    def parse_file(self) -> None:
        """Go through input file and extract all relevant parameters"""
        prm_kws = ['min', 'max', 'update', 'stop_when']
        gof = False
        xdd = False
        in_xdd = False
        xdd_count = 0
        macro = False
        current_macro = []
        in_lam = False 
        current_lambda = []
        in_bkg = False
        current_bkg = []
        in_xdd_macro = False
        lcount = 0
        rcount = 0
        self.defines = set()
        define = False
        ifdef = False
        in_ifdef = False
        in_str = False
        current_str = []
        updated_str = False
        in_prm = False
        prm = False
        current_prm = []
        in_eqn = False
        for line in self.uncommented_string:
            for s in line.split():
                if s == '#ifdef':
                    ifdef = True
                    continue
                if ifdef:
                    ifdef = False
                    if s not in self.defines:
                        in_ifdef = True
                        continue
                if in_ifdef:
                    if s == '#endif':
                        in_ifdef = False
                        continue
                    continue
                if s == 'prm':
                    if in_prm:
                        self.prms.update({current_prm_name : PRM(current_prm)})
                        current_prm = []
                    in_prm = True
                    prm = True
                    continue
                if in_prm:
                    if prm:
                        current_prm.append(s)
                        current_prm_name = s
                        prm = False
                        continue
                    else:
                        if '=' in s:
                            current_prm.append(s)
                            in_eqn = True
                            if ';' in s:
                                in_eqn = False
                            continue
                        else:
                            if ';' in s:
                                current_prm.append(s)
                                in_eqn = False
                                continue
                            if in_eqn:
                                current_prm.append(s)
                                continue
                            else:
                                if s[0].isalpha() or s[0] == '#':
                                    if s in prm_kws:
                                        current_prm.append(s)
                                        continue
                                    in_prm = False
                                    self.prms.update({current_prm_name : PRM(current_prm)})
                                    current_prm = []
                                else:
                                    current_prm.append(s)
                                    continue
                if in_xdd:
                    if op:
                        xdd_now.other_props[op_kw] = Value(s).value
                        op = False
                        continue
                    if s in xdd_now.other_props:
                        op = True
                        op_kw = s
                        continue
                    if s == 'lam':
                        in_lam = True
                        continue
                    if in_lam:
                        if Source.in_lambda(s):
                            current_lambda.append(s)
                        else:
                            self.xdds[xdd_count-1].set_lambda(current_lambda)
                            current_lambda = []
                            in_lam = False
                    if s == 'bkg':
                        in_bkg = True
                        continue
                    if in_bkg:
                        if BKG.in_bkg(s):
                            current_bkg.append(s)
                            continue
                        else:
                            self.xdds[xdd_count-1].set_bkg(current_bkg)
                            current_bkg = []
                            in_bkg = False
                    if s.split('(')[0] in self.xdds[xdd_count-1].macros:
                        mac_name = s.split('(')[0] 
                        in_xdd_macro = True
                    if in_xdd_macro:
                        current_macro.append(s)
                        lcount += s.count('(')
                        rcount += s.count(')')
                        if rcount == lcount:
                            if mac_name[0] == 'Z':
                                self.xdds[xdd_count-1].set_ZE(current_macro)
                            elif mac_name == 'LP_Factor':
                                self.xdds[xdd_count-1].set_LPfactor(current_macro)
                            elif mac_name == 'Simple_Axial_Model' or mac_name == 'Full_Axial_Model':
                                self.xdds[xdd_count-1].set_axial_model(current_macro)
                            current_macro = []
                            in_xdd_macro = False
                            lcount = 0
                            rcount = 0
                            continue
                        continue
                    if s == 'str':
                        in_str = True
                        updated_str = False
                        if len(current_str):
                            self.xdds[xdd_count-1].add_str(current_str)
                            current_str = []
                        continue
                    if len(s) > 3 and s[:4] == 'STR(':
                        in_str = True
                        updated_str = False
                        if len(current_str):
                            self.xdds[xdd_count-1].add_str(current_str)
                        current_str = [s]
                        continue
                if s == 'xdd':
                    if in_str:
                        if len(current_str):
                            self.xdds[xdd_count-1].add_str(current_str)
                            updated_str = True
                        in_str = False
                    xdd = True
                    xdd_count += 1
                    in_xdd = False
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
                if s == 'macro':
                    macro = True
                    continue
                if macro:
                    current_macro.append(s)
                    if '}' in s:
                        macro = False
                        new_macro = Macro(current_macro)
                        self.macros.update({new_macro.name : new_macro})
                        current_macro = []
                    continue
                if s == "#define":
                    define = True
                    continue
                if define:
                    self.defines.add(s)
                    define = False
                    continue
                if gof:
                    self.gof_params[gof_kw] = float(s)
                    gof = False
                    continue
                if s in self.gof_params:
                    gof = True
                    gof_kw = s
                    continue
                if in_str:
                    current_str.append(s)
        if not updated_str:
            self.xdds[xdd_count-1].add_str(current_str)

    def reset_gof_params(self) -> None:
        """Reset the goodness of fit parameters to zero"""
        self.gof_params = {'r_exp' : 0.,
                           'r_wp' : 0.,
                           'r_p' : 0.,
                           'r_exp_dash' : 0.,
                           'r_wp_dash' : 0.,
                           'r_p_dash' : 0.,
                           'weighted_Durbin_Watson' : 0.,
                           'gof' : 0.,}

class XDD:
    """Class to hold data relating to analysis of a dataset"""
    def __init__(self, fname : str) -> None:
        """
        Args:
            fname (str): filename of experimental data
        """
        self._fname = fname
        self.strucs = []
        self.other_props = {'start_X' : 0.,
                            'finish_X' : 0.,
                            'x_calculation_step' : 0.}
        self.macros = {'ZE', 'Zero_Error', 'LP_Factor',
                       'Simple_Axial_Model',
                       'Full_Axial_Model'}
        self.structures = dict()
    
    def set_lambda(self, lambda_text : str) -> None:
        """Set the source information
        
        Args:
            lambda_text (str) : text from input file relating to source characteristics
        """
        self.source = Source(lambda_text)
    
    def set_bkg(self, bkg_text : str) -> None:
        """Set Chebyshev background information for dataset
        
        Args:
            bkg_text (str): text from input file relating to Chebyshev background parameters
        """
        self.bkg = BKG(bkg_text)
    
    def set_ZE(self, ze_text : str) -> None:
        """Set Zero Error information for dataset
        
        Args:
            ze_text (str): text from input file relating to zero error
        """
        self.ze = Macro(ze_text)
    
    def set_axial_model(self, am_text : str) -> None:
        """Set axial model information for dataset
        
        Args:
            am_text (str): text from input file relating to axial model
        """
        self.axial_model = Macro(am_text)
    
    def set_LPfactor(self, lp_text : str) -> None:
        """Set Lorentz polarization information for dataset
        
        Args:
            lp_text (str): text from input file relating to Lorentz polarization
        """
        self.lpfactor = Macro(lp_text)
    
    def add_str(self, str_text : list) -> None:
        """Add a structure information block
        
        Args:
            str_text (list): list of strings from input file relating to structure
        """
        struc = STR(str_text)
        self.structures.update({struc.phase_name : struc})

class STR:
    """Class to parse and hold structural information data"""
    def __init__(self, str_text : list) -> None:
        """
        Args:
            str_text (list) : list of strings from input file relating to structure
        """
        self.phase_name = None
        self.str_text = ' '.join(str_text)
        self.parse_str(str_text)
    
    def parse_str(self, str_text : list) -> None:
        """Parse structural information from input file
        Args:
            str_text (list) : list of strings from input file relating to structure
        """
        phase_name = None
        space_group = None
        pn = False
        sg = False
        in_macro = False
        for s in str_text:
            if len(s) > 3 and s[:4] == 'STR(': 
                in_macro = True
                sg = True 
                new_s = s[4:]
                new_s = new_s.split(',')
                if not new_s[0]: 
                    continue
                if new_s[0][-1] == ')':
                    if '"' in new_s[0]:
                        space_group = new_s[0].split('"')[1]
                    else:
                        space_group = new_s[0][:-1]
                    sg = False
                    in_macro = False
                    continue
                if '"' in new_s[0]:
                    space_group = new_s[0].split('"')[1]
                else:
                    space_group = new_s[0]
                sg = False
                if len(new_s) == 1:
                    continue
                if '"' in new_s[1]:
                    phase_name = new_s[1].split('"')[1]
                    in_macro = False
                    continue
                else:
                    if new_s[1]:
                        if new_s[1][-1] == ')':
                            phase_name = new_s[1][:-1]
                        else:
                            phase_name = new_s[1]
                        in_macro = False
                        continue
                    pn = True
                    continue
            if in_macro:
                if s == ',':
                    pn = True
                    continue
                else:
                    if s[0] == ',':
                        pn = True
                        s = s[1:]
                if sg:
                    new_s = s.split(',')
                    if '"' in new_s[0]:
                        space_group = new_s[0].split('"')[1]
                    else:
                        if new_s[0][-1] == ')':
                            space_group = new_s[0][:-1]
                            in_macro = False
                        else:
                            space_group = new_s[0]
                    sg = False
                    if len(new_s) > 1:
                        if len(new_s[1]):
                            if '"' in new_s[1]:
                                phase_name = new_s[1].split('"')[1]
                            else:
                                if new_s[1][-1] == ')':
                                    phase_name = new_s[1][:-1]
                                else:
                                    phase_name = new_s[1]
                            in_macro = False
                        else:
                            pn = True
                        continue
                    continue
                if pn:
                    if '"' in s:
                        phase_name = s.split('"')[1]
                    else:
                        if s[-1] == ')':
                            phase_name = s[:-1]
                        else:
                            phase_name = s
                    in_macro = False
                    pn = False
                    continue
                new_s = s.split(',')
                if len(new_s) == 1:
                    in_macro = False
                    continue
            if s == "phase_name":
                pn = True
                continue
            if s == "space_group":
                sg = True
                continue
            if pn:
                if '"' in s:
                    phase_name = s.split('"')[1]
                else:
                    phase_name = s
                pn = False
                continue
            if sg:
                if '"' in s:
                    space_group = s.split('"')[1]
                else:
                    space_group = s
                sg = False
                continue
        self.phase_name = "Unknown_phase" if phase_name is None else phase_name
        self.space_group = "P1" if space_group is None else space_group

class BKG:
    """Class to hold Chebyshev background information"""
    def __init__(self, bkg_text : list) -> None:
        """
        Args:
            bkg_text (list): list of strings from input file relating to Chebyshev
            background.
        """
        self.bkg_text = ' '.join(bkg_text)

    @staticmethod
    def in_bkg(s : str) -> bool:
        """Return boolean for whether string could be part of background or not
        
        Args:
            s (str): string about which to determine if possibly background parameter
        """
        if s[0].isdigit() or s[0] == '-' or s[0] == '@':
            return True
        return False
    
class Source:
    """Class to hold (X-ray) source information"""
    def __init__(self, lambda_text : list) -> None:
        """
        Args:
            lambda_text (list): list of strings from input file relating to source 
        """
        self.lambda_text = ' '.join(lambda_text)

    @staticmethod
    def in_lambda(s : str) -> bool:
        """Return boolean for whether string could be part of source info or not
        
        Args:
            s (str): string about which to determine if possibly source parameter
        """
        if s in ['la', 'lo', 'lh', 'lg', 'ymin_on_ymax']:
            return True
        if s[0].isdigit():
            return True
        return False

class PRM:
    """Class to hold parameter information"""
    def __init__(self, prm_text : list) -> None:
        """
        Args:
            prm_text (list): list of strings from input file relating to parameter
        """
        self.prm_text = prm_text
        self.get_name()
    
    def get_name(self) -> None:
        """Assign parameter name from prm information"""
        self.name = self.prm_text[1]

class Macro:
    def __init__(self, macro : list) -> None:
        """Class to hold (minimal) TOPAS macro information
        
        Args:
            macro (list): list of strings from input file defining macro
        """
        self.macro = macro
        self.macro_text = ' '.join(macro)
        self.get_name()
    
    def get_name(self) -> None:
        """Assign macro name from macro information"""
        self.name = self.macro[0].split('(')[0]

class Value:
    """Class to parse and hold a parameter value (with associated uncertainty)"""
    def __init__(self, value_text : str) -> None:
        """
        Args:
            value_text (str): string with value text from input file
        """
        self.value_text = value_text
        self.parse_value()
    
    def parse_value(self) -> None:
        """Assign value and uncertainty quantities"""
        if '_LIMIT' in self.value_text:
            self.value_text = self.value_text[:self.value_text.index('_L')]
        if '`' in self.value_text:
            vals = self.value_text.split('`_')
        else:
            vals = self.value_text.split('_')
        self.value = float(vals[0])
        if len(vals) == 2:
            self.std = float(vals[1])
        else:
            self.std = 0.