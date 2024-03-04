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