import pytest
from topaspy import Input
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