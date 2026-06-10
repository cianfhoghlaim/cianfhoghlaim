import re
from dictutils import featureStringToDict

#########################################################################
# UDToken class                                                         #
#########################################################################

class UDToken:
  
  labels = ('index','token','lemma','upos','xpos','morph','head','deprel','enh','other')
  
  def __init__(self, lineNumber=None, line=None):
    if line==None:
      line="0\tROOT"+"\t_"*8
    self._lineNumber = lineNumber
    self._data = {k: v for (k, v) in zip(UDToken.labels,line.split('\t'))}
    self._head = None         # will be a Token object once sentence is read
    self._predecessor = None  # also a Token
    self._deps = list()
    self._featDict = featureStringToDict(self._data['morph'])
    # TODO: warnings are just strings for now, but probably want a full object
    # representing all needed metadata for each error for reporting
    self._warnings = list()
    self._verified = dict()

  # Can pass conllu field names *or* feature names
  # Returns None if feature value is not set
  # Note that it returns a list in case of a feature name
  def __getitem__(self, arg):
    if arg == 'index' or arg == 'head':
      if self.isMultiwordToken():
        raise ValueError('Should not be accessing index or head of a multiword token')
      else:
        return int(self._data[arg])
    elif arg == 'deprel' and self._data['deprel']=='compound':
      return 'nmod'
    elif arg in UDToken.labels:
      return self._data[arg]
    elif arg in self._featDict:
      return self._featDict[arg].split(',')
    else:
      return None

  def isMultiwordToken(self):
    return bool(re.match('[0-9]+-', self._data['index']))

  def addWarning(self, problem):
    if problem != '':
      locator = '[Line '+str(self._lineNumber)+' '+str(self)+']: '
      self._warnings.append(locator+problem)

  def runChecks(self, lexicon):
    if self.isMultiwordToken():
      return

    self.addWarning(lexicon.lookup(self))

    for toCheck in self.checkableFeatures():
      if toCheck in self._verified:
        continue
      constraintList = self.predictFeatureValue(toCheck)
      if len(constraintList)==0:
        self.addWarning('Warning: no constraints found for feature '+toCheck)
      else:
        for constraint in constraintList:
          if not constraint.isSatisfied(self[toCheck]):
            self.addWarning(constraint.getMessage())

  def predictFeatureValue(self, feat):
    raise NotImplementedError('should only be called for specific language')

  def checkableFeatures(self):
    raise NotImplementedError('should only be called for specific language')
    
  # use self._data['index'] so it works for MWTs also
  def __str__(self):
    return '('+self._data['index']+','+self['token']+','+self['lemma']+','+self['upos']+')'

  def conlluString(self):
    return '\t'.join(self._data[k] for k in UDToken.labels)
      
  def reportString(self):
    return '\n'.join(self._warnings)

  def isRoot(self):
    return not self.isMultiwordToken() and self['index']==0

  def isAnyNominal(self):
    return (self['upos']=='NOUN' or self['upos']=='PROPN' or self['upos']=='PRON')

  def isNominal(self):
    return (self['upos']=='NOUN' or self['upos']=='PROPN')

  def setHead(self, headToken):
    self._head = headToken

  def getHead(self):
    return self._head

  # getHead, but recurses through coordinations
  def getUltimateHead(self):
    if self['deprel']=='conj':
      return self._head.getUltimateHead()
    else:
      return self._head

  def setPredecessor(self, predToken):
    self._predecessor = predToken

  # returns None if self is the root token, otherwise != None
  def getPredecessor(self):
    return self._predecessor

  # skip quotation marks
  def getRealPredecessor(self):
    pr = self.getPredecessor()
    if pr==None or pr['lemma'] not in ["'", "''", '"', '“', '”', '‘', '’']:
      return pr
    else:
      return pr.getRealPredecessor()

  def addVerified(self, vdict):
    self._verified = vdict

  def addDependent(self, depToken):
    self._deps.append(depToken)

  def getDependents(self):
    return self._deps

  # used to recurse over coordinations but that's not really what we want
  def isInPP(self):
    return any(t['upos']=='ADP' and t['deprel']=='case' for t in self._deps)

  def _recomputeFeatureString(self):
    self._data['morph'] = '|'.join(k+'='+self._featDict[k] for k in sorted(self._featDict) if k[0]!='X')
  
  def addFeature(self, featName, featVal):
    vals = []
    if featName in self._featDict:
      vals = self._featDict[featName].split(',')
    if featVal not in vals:
      vals.append(featVal)
      vals.sort()
      self._featDict[featName] = ','.join(vals)
      self._recomputeFeatureString()

  def killFeature(self, featName, featVal):
    if featName in self._featDict:
      vals = self._featDict[featName].split(',')
      if featVal in vals:
        vals.remove(featVal)
        if len(vals) > 0:
          self._featDict[featName] = ','.join(vals)
          self._recomputeFeatureString()
        else:
          del self._featDict[featName]
        self._recomputeFeatureString()

  # just used in dictutils.py
  def getFeatureDict(self):
    return self._featDict

  def has(self, feature, featureVal):
    return feature in self._featDict and featureVal in self._featDict[feature]

  def getDeprel(self):
    return self['deprel']

  def getUltimateDeprel(self):
    ans = self['deprel']
    if ans=='conj':
      return self._head.getUltimateDeprel()
    else:
      return ans

  # overridden for Irish (tAcht -> t-acht), potentially others
  def lowerToken(self):
    return self['token'].lower()

  __repr__ = __str__
