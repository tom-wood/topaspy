import pytest
from topaspy import Input, STR
import os
from os.path import join

pwd = os.path.dirname(os.path.abspath(__file__))
data_fpath = join(pwd, './data/')

class TestInput:
    @pytest.fixture(autouse=True)
    def init_input(self):
        self.inst = Input(f"{data_fpath}/test.inp")
    
    def test_fpath(self):
        assert self.inst.fname.split('/')[-1] == "test.inp"
        with pytest.raises(FileNotFoundError):
            self.inst.fname = "nonsense.inp"
    
    def test_remove_line_comment(self):
        s0 = "xdd'another comment"
        s1 = "'"
        s2 = "xdd"
        s3 = "xdd'comment'and another"
        assert self.inst.remove_line_comment(s0) == "xdd"
        assert self.inst.remove_line_comment(s1) == ""
        assert self.inst.remove_line_comment(s2) == "xdd"
        assert self.inst.remove_line_comment(s3) == "xdd"
    
    def test_remove_comments(self):
        s0 = "xdd'another comment\n/*\nother*/"
        s1 = "'comment\nxdd/*other*/\n"
        assert ''.join(self.inst.remove_comments(s0)) == "xdd"
        assert ''.join(self.inst.remove_comments(s1)) == "xdd"
    
    def test_parse_file(self):
        self.inst.parse_file()
        ps = self.inst.gof_params
        assert ps['r_exp'] == 10.8867021
        assert ps['r_wp'] == 17.080898
        assert ps['r_p'] == 13.0440099
        assert ps['r_exp_dash'] == 13.1325639                                                      
        assert ps['r_wp_dash'] == 20.6045854 
        assert ps['r_p_dash'] == 16.4280403
        assert ps['weighted_Durbin_Watson'] == 1.50548645
        assert ps['gof'] == 1.56896898
        xdd = self.inst.xdds[0]
        ops = xdd.other_props
        assert ops['start_X'] == 2.5
        assert ops['finish_X'] == 86.0
        assert ops['x_calculation_step'] == 0.002
        assert len(self.inst.macros) == 3
        assert all([f"test_macro{n}" in self.inst.macros for n in [1, 2, 3]])
        assert len(xdd.source.lambda_text.split()) == 10
        assert len(xdd.bkg.bkg_text.split()) == 5
        assert xdd.ze.name == "Zero_Error"
        assert xdd.lpfactor.name == "LP_Factor"
        assert xdd.axial_model.name == "Simple_Axial_Model"
        assert "FE4N" in self.inst.defines
        assert "NA2O" in self.inst.defines
        assert "Fe4N" in xdd.structures
        assert "Na2O" in xdd.structures

class TestSTR:
    @pytest.fixture(autouse=True)
    def init_STR(self):
        self.inst = STR([''])

    def test_parse_str(self):
        n = 8
        sg_inps = ['Pm-3m', '"Pm-3m"']
        sg_inps0 = ['Pm-3m', ' Pm-3m', 'Pm-3m ', ' Pm-3m ',
                    '"Pm-3m"', ' "Pm-3m"', '"Pm-3m" ', ' "Pm-3m" ']
        for sgi in sg_inps0:
            inp = f"STR({sgi})"
            self.inst.parse_str(inp.split())
            assert self.inst.space_group == 'Pm-3m'
            assert self.inst.phase_name == 'Unknown_phase'
        for sgi in sg_inps:
            inp = f'space_group {sgi}'
            self.inst.parse_str(inp.split())
            assert self.inst.space_group == 'Pm-3m'
            assert self.inst.phase_name == 'Unknown_phase'
        pn_inps = ['phase1', '"phase1"']
        for pni in pn_inps:
            inp = f'phase_name {pni}'
            self.inst.parse_str(inp.split())
            assert self.inst.space_group == 'P1'
            assert self.inst.phase_name == 'phase1'
