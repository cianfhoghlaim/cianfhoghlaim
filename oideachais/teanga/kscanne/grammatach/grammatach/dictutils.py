import re

def featureStringToDict(features):
  ans = dict()
  if features != '_':
    for featurepair in features.split('|'):
      k,v = featurepair.split('=')
      ans[k] = v
  return ans

def isSubset(featDict1, featDict2):
  return all(k in featDict2 and featDict1[k]==featDict2[k] for k in featDict1)

class UDDictionary:

  def __init__(self, fileName=None):
    # keys are surface forms, values are dictionaries whose keys
    # are possible lemmas for that surface form and whose values
    # are more dictionaries. Keys of those dictionaries are possible
    # POS tags for the given surface/lemma pair, and whose values
    # are a list of dictionaries of feature/feature-values
    self._words = dict()
    if fileName != None:
      self._readFromFile(fileName)

  def _readFromFile(self, fileName):
    with open(fileName) as f:
      for line in f:
        line = line.rstrip('\n')
        fields = line.split('\t')
        if fields[0] not in self._words:
          self._words[fields[0]] = dict()
        if fields[1] not in self._words[fields[0]]:
          self._words[fields[0]][fields[1]] = dict()
        if fields[2] not in self._words[fields[0]][fields[1]]:
          self._words[fields[0]][fields[1]][fields[2]] = list()
        self._words[fields[0]][fields[1]][fields[2]].append(featureStringToDict(fields[4]))
      f.close()

  # return '' if everything is OK and an error message if not
  def lookup(self, tok):
    if not self._words:
      return ''
    surf = tok['token']
    if tok['lemma'].islower() and not surf.islower():
      surf = self.lowerToken()
    if tok['upos'] in ['PROPN', 'PUNCT', 'SYM', 'X']:
      return ''
    if tok['upos']=='NUM' and re.search('[0-9]',surf):
      return ''
    if tok.has('Typo','Yes'):
      return ''
    if surf not in self._words:
      return str(tok)+' Surface token not in lexicon'
    if tok['lemma'] not in self._words[surf]:
      return str(tok)+' Known surface form, but lemma not in lexicon'
    if tok['upos'] not in self._words[surf][tok['lemma']]:
      return str(tok)+' Known surface form and lemma, but not with this POS'
    if not any(isSubset(lexFeatDict, tok.getFeatureDict()) for lexFeatDict in self._words[surf][tok['lemma']][tok['upos']]):
      return str(tok)+' No feature set in lexicon for this surface/lemma/POS matches token feats'
    return ''
