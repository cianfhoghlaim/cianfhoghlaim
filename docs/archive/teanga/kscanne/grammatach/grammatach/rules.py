import re
class Constraint:

  # value is a string; either a single feature value like "Len"
  # or else a pipe-separated set of options: "Ecl|Len"
  # This asserts that at least one of the piped values *must* be there
  # (despite the slightly confusing attribute name "permitted")
  # "None" is permitted as a feature value; if it appears alone,
  # then the constraint means the feature should not appear at all.
  # If it appears piped together with other values, e.g. "Ecl|Len|None",
  # then the other values might appear, but not necessarily.
  # Also allowed to specify a negated feature value (other than "None"):
  # for example, "!Len" means that Len should *not* appear for this feature.
  # NB Doesn't make sense to have more than one negated term, since that
  # would then allow anything; we prefer listing all permitted values
  # in that case, together with "None": "Ecl|Len|None"
  def __init__(self, value, message):
    asList = value.split('|')
    self._forbidden = set(x[1:] for x in asList if x.startswith('!'))
    self._permitted = set(x for x in asList if not x.startswith('!'))
    self._message = message

  # pass list of feature values (so, ['Len'] or ['Ecl','Emp'], usually,
  # but also None if feature not set) and
  # return True iff this constraint is satisfied
  def isSatisfied(self, udValues):
    if udValues==None:
      return 'None' in self._permitted or len(self._forbidden)>0
    else:
      return any(val in self._permitted for val in udValues) or \
             any(val not in udValues for val in self._forbidden)

  # slight variant of previous method
  # here, we pass a single feature value that appears in UD file
  # (so, just "Len", or "Emp", never None)
  # and return True iff constraint explains existence of this feature value
  # NB we don't allow negations to explain features; this is important in cases
  # where multiple values are allowed (e.g. !Len doesn't explain Emp)
  def explainsValue(self, oneValue):
    return oneValue in self._permitted

  def getMessage(self):
    return self._message
  
  def __str__(self):
    return 'Constraint that feature value ' + '|'.join(self._permitted) + ' must appear'
