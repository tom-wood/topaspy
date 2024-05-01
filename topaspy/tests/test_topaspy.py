import pytest
from topaspy import Input, STR, Value, PRM, Equation, BKG
import os
from os.path import join

pwd = os.path.dirname(os.path.abspath(__file__))
data_fpath = join(pwd, './data/')

class TestInput:
    @pytest.fixture(autouse=True)
    def init_input(self) -> None:
        self.inst = Input(f"{data_fpath}/test.inp")
    
    def test_fpath(self) -> None:
        assert self.inst.fname.split('/')[-1] == "test.inp"
        with pytest.raises(FileNotFoundError):
            self.inst.fname = "nonsense.inp"
    
    def test_remove_line_comment(self) -> None:
        s0 = "xdd'another comment"
        s1 = "'"
        s2 = "xdd"
        s3 = "xdd'comment'and another"
        assert self.inst.remove_line_comment(s0) == "xdd"
        assert self.inst.remove_line_comment(s1) == ""
        assert self.inst.remove_line_comment(s2) == "xdd"
        assert self.inst.remove_line_comment(s3) == "xdd"
    
    def test_remove_comments(self) -> None:
        s0 = "xdd'another comment\n/*\nother*/"
        s1 = "'comment\nxdd/*other*/\n"
        assert ''.join(self.inst.remove_comments(s0)) == "xdd"
        assert ''.join(self.inst.remove_comments(s1)) == "xdd"
    
    def test_parse_file(self) -> None:
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
        assert(len(self.inst.xdds)) == 2
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
        for i in range(5):
            assert f"random_prm{i}" in self.inst.prms
        assert sum(xdd.bkg.coefficients) == 1.7356125646

class TestSTR:
    @pytest.fixture(autouse=True)
    def init_STR(self) -> None:
        self.inst = STR([''])

    def test_parse_str(self) -> None:
        n = 8
        sg_inps = ['Pm-3m', '"Pm-3m"']
        sg_inps0 = ['Pm-3m', ' Pm-3m', 'Pm-3m ', ' Pm-3m ',
                    '"Pm-3m"', ' "Pm-3m"', '"Pm-3m" ', ' "Pm-3m" ']
        for sgi in sg_inps0:
            inp = f'STR({sgi})'
            self.inst.parse_str(inp.split())
            assert self.inst.space_group == 'Pm-3m'
            assert self.inst.phase_name == 'Unknown_phase'
        for sgi in sg_inps:
            inp = f'space_group {sgi}'
            self.inst.parse_str(inp.split())
            assert self.inst.space_group == 'Pm-3m'
            assert self.inst.phase_name == 'Unknown_phase'
        pn_inps = ['phase1', '"phase1"']
        pn_inps0 = ['phase1', ' phase1', 'phase1 ', ' phase1 ',
                    '"phase1"', ' "phase1"', '"phase1" ', ' "phase1" ']
        for pni in pn_inps:
            inp = f'phase_name {pni}'
            self.inst.parse_str(inp.split())
            assert self.inst.space_group == 'P1'
            assert self.inst.phase_name == 'phase1'
        from itertools import product
        sg_inps1 = [f'space_group {sgi}' for sgi in sg_inps]
        pn_inps1 = [f'phase_name {pni}' for pni in pn_inps]
        for inp1, inp2 in product(sg_inps1, pn_inps1):
            inp = f'{inp1} {inp2}'
            self.inst.parse_str(inp.split())
            assert self.inst.space_group == 'Pm-3m'
            assert self.inst.phase_name == 'phase1'
        for sgi, pni in product(sg_inps0, pn_inps0):
            inp = f'STR({sgi},{pni})'
            print(inp)
            self.inst.parse_str(inp.split())
            assert self.inst.space_group == 'Pm-3m'
            assert self.inst.phase_name == 'phase1'

class TestValue:
    def test_parse_value(self) -> None:
        vals = ['1.0', '1.0_LIMIT_MIN_0.1',
                '1.0_LIMIT_MAX_1.4',
                '1.0`_0.1', '1.0`_0.1_LIMIT_MIN_0.1',
                '1.0`_0.1_LIMIT_MAX_1.4',
                '1.0_0.1']
        for i, val in enumerate(vals):
            val_example = Value(val)
            assert val_example.value == 1.0
            if i < 3:
                assert val_example.std == 0.0
            else:
                assert val_example.std == 0.1

class TestParameter:
    @pytest.fixture(autouse=True)
    def init_PRM(self) -> None:
        prm_strs = ['prm random_prm0 45.0',
                    'prm random_prm1 = 45.0 * 1;',
                    'prm random_prm2 = 45.0 * 1; : 45.0',
                    'prm random_prm3 = random_prm2 * 1; : 45.0',
                   ]
        prms = [PRM(s.split()) for s in prm_strs]
        self.insts = dict([(p.name, p) for p in prms])
    
    def test_get_name(self) -> None:
        for i, prm in enumerate(self.insts):
            assert self.insts[prm].name == f"random_prm{i}"

class TestEquation:
    @pytest.fixture(autouse=True)
    def init_eqn(self) -> None:
        eqn_strs = ['=17* 54;', '= 83 * occ_H1 - 3; : 42.08']
        self.insts = [Equation(eqn.split()) for eqn in eqn_strs]
        self.answers = [None, 42.08]
    
    def test_parse_equation(self) -> None:
        for ans, inst in zip(self.answers, self.insts):
            if ans is None:
                assert inst.value is None
            else:
                assert inst.value.value == ans

class TestBKG:
    @pytest.fixture(autouse=True)
    def init_bkg(self) -> None:
        bkg_strs = ['bkg @ 0 0 0 0',
                    '@ 1.5`_0.4 2.5`_0.7']
        self.insts = [BKG(bs.split()) for bs in bkg_strs]
        self.sums = [0, 4.0]
        self.sum_stds = [0, 1.1]
    
    def test_parse_bkg(self) -> None:
        for inst, cs, css in zip(self.insts, self.sums, self.sum_stds):
            assert sum(inst.coefficients) == cs
            assert sum([v.std for v in inst.values]) == css