import unittest
from testquery import checkquery
from testquery import testdbname
from generate_test_relations import generate_default
from raco.language import CCAlgebra

import sys
import os
sys.path.append('./examples')
from emitcode import emitCode
from osutils import Chdir

# skipping
from nose.tools import nottest


class ClangTest(unittest.TestCase):
    def check(self, query, name):
        chdir = Chdir("c_test_environment")
        emitCode(query, name, CCAlgebra)
        checkquery(name)

    def setUp(self):
        chdir = Chdir("c_test_environment")
        if not os.path.isfile(testdbname()):
            generate_default()  
        
    @nottest
    def test_scan(self):
        self.check("A(s1) :- T1(s1)", "scan")

    @nottest
    def test_select(self):
        self.check("A(s1) :- T1(s1), s1>5", "select") 

    @nottest
    def test_join(self):
        self.check("A(s1,o2) :- T3(s1,p1,o1), R3(o2,p1,o2)", "join")
            
    @nottest
    def test_select_conjunction(self):
        self.check("A(s1) :- T1(s1), s1>0, s1<10", "select_conjunction"),


if __name__ == '__main__':
    unittest.main()
