import boolean
import rules
import algebra
from language import Language

import os.path

class CC(Language):
  @staticmethod
  def assignment(x, y):
    return "%s = %s;" % (x,y)

  @staticmethod
  def initialize(resultsym):
    return  initialize % locals()

  @staticmethod
  def finalize(resultsym):
    return  finalize % locals()

  @classmethod
  def boolean_combine(cls, args, operator="&&"):
    opstr = " %s " % operator 
    conjunc = opstr.join(["(%s)" % cls.compile_boolean(arg) for arg in args])
    return "( %s )" % conjunc

  """
  Expects unnamed perspective
  """
  @staticmethod
  def compile_attribute(position):
    return 'tuple[%s]' % position

"""
Replace column names with positions
"""
def unnamed(condition, sch):
  if isinstance(condition, boolean.BinaryBooleanOperator): 
    condition.left = unnamed(condition.left, sch)
    condition.right = unnamed(condition.right, sch)
    return condition
  elif isinstance(condition, boolean.Attribute):
    # replace the attribute name with it's position in the relation
    pos = sch.getPosition(condition.name)
    return boolean.Attribute(pos)
  else:  
    # do nothing; it's a literal or something custom
    return condition

class CCOperator:
  language = CC

class FileScan(algebra.Scan, CCOperator):
  def compileme(self, resultsym):
    name = self.name
    code = scan_template % locals()
    return code

class TwoPassSelect(algebra.Select, CCOperator):
  def compileme(self, resultsym, inputsym):
    pcondition = unnamed(self.condition, self.scheme())
    condition = CC.compile_boolean(pcondition)
    code = """

bool condition_%(inputsym)s(const Tuple *tuple) {
  return %(condition)s
}

TwoPassSelect(&condition_%(inputsym)s, %(inputsym)s, %(resultsym)s);

""" % locals()
    return code

class TwoPassHashJoin(algebra.Join, CCOperator):
  def compileme(self, resultsym, leftsym, rightsym):
    if len(self.attributes) > 1: raise ValueError("The C compiler can only handle equi-join conditions of a single attribute")
 
    leftattribute, rightattribute = self.attributes[0]
    leftattribute = CC.compile_attribute(leftattribute)
    rightattribute = CC.compile_attribute(rightattribute)
    
    code = """

HashJoin(&condition_%(inputsym)s, %(inputsym)s, %(resultsym)s);

""" % locals()

    return code

class CCAlgebra:
  language = CC

  operators = [
  TwoPassHashJoin,
  TwoPassSelect,
  FileScan
]
  rules = [
  rules.OneToOne(algebra.Join,TwoPassHashJoin),
  rules.OneToOne(algebra.Select,TwoPassSelect),
  rules.OneToOne(algebra.Scan,FileScan)
]
 