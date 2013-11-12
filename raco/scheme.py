import boolean
from collections import OrderedDict
import expression

class DummyScheme:
  """Dummy scheme used to generate plans in the absence of catalog info."""
  def __len__(self):
    return 0

  def __repr__(self):
    return "DummyScheme"

class Scheme:
  '''
Add an attribute to the scheme
Type is a function that returns true for any value that is of the correct type
  '''
  salt = "1"
  def __init__(self,attributes=None):
    if attributes is None:
      attributes = []
    self.attributes = []
    self.asdict = OrderedDict()
    for n,t in attributes:
      self.addAttribute(n,t)

  def addAttribute(self, name, type):
    if self.asdict.has_key(name):
      # ugly.  I don't like throwing errors in this case, but it's worse not to
      return self.addAttribute(name + self.salt, type)
    self.asdict[name] = (len(self.attributes), type)
    self.attributes.append((name,type))
    # just in case we changed the name.  ugly.
    return name

  def typecheck(self, tup):
    try:
      return all([tf(v) for (n,tf),v in zip(self.attributes,tup)])
    except:
      raise TypeError("%s not of type %s" % (tup,self.attributes))

  def __eq__(self, other):
    return self.attributes == other.attributes

  def getPosition(self, name): 
    return self.asdict[name][0]
  
  def getName(self, position):
    return self[position][0]

  def getType(self, name):
    if type(name) == int:
      return self[name][1]
    else:
      return self.asdict[name][1]

  def subScheme(self, attributes):
    """Return a scheme consisting of only the provided attribute names"""
    return Scheme([(n,self.getType(n)) for n in attributes])

  def subsumes(self, names):
    """Does this scheme contain all the names in the list?"""
    return all([n in self.asdict.keys() for n in names])

  def contains(self, names):
    """deprecated.  use subsumes"""
    return self.contains(names)

  def resolve(self, attrref):
    """return the name and type of the attribute reference, resolved against this scheme"""
    unnamed = expression.toUnnamed(attrref,self)
    return self.getName(unnamed.position), self.getType(unnamed.position)

  def ascolumnlist(self):
    """Return a columnlist structure suitable for use with Project and ProjectingJoin.
    Currently a list of positional attribute references.  May eventually be a scheme itself.
    """
    return [expression.UnnamedAttributeRef(i) for i in xrange(len(self))]

  def __contains__(self, attr, typ=None):
    if typ:
      return (attr,type) in self.attributes
    else:
      return attr in self.asdict

  def project(self, tup, subscheme):
    """Return a tuple corresponding to the subscheme corresponding to the values in tup"""
    return (tup[self.getPosition(n)] for n,t in subscheme.attributes)

  def rename(self, name1, name2):
    try:
      i,t = self.asdict.pop(name1)
      self.attributes[i] = (name2, t)
      self.asdict[name2] = (i,t)
    except KeyError:
      pass

  def __str__(self):
    """Pretty print the scheme"""
    return str(self.attributes)

  def __len__(self):
    """Return the number of attributes in the scheme"""
    return len(self.attributes)

  def __iter__(self):
    return self.attributes.__iter__()

  def __getitem__(self, key):
    return self.attributes.__getitem__(key)

  def __add__(self, other):
    newsch = Scheme(self.attributes)
    for (n,t) in other:
      newsch.addAttribute(n,t)
    return newsch

  def __sub__(self, other):
    newsch = Scheme()
    for (n,t) in self:
      if not n in other: 
        newsch.addAttribute(n,t)
    return newsch

  def __str__(self):
    return str(self.attributes)


class EmptyScheme(Scheme):
  def __init__(self):
    Scheme.__init__(self, [])

