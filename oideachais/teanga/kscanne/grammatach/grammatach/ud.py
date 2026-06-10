import re
from dictutils import UDDictionary
from factory import TokenFactory

#########################################################################
# UDSentence class                                                      #
#########################################################################

class UDSentence:

  def __init__(self, languageCode):
    self._comments = list()
    self._factory = TokenFactory(languageCode)
    self._tokens = [self._factory.createToken()]
    self._sentID = None
    # keys are UD token indices, values are indices in list self._tokens
    self._index2index = {0: 0}

  # lineNumber is the previously-read line number from this stream
  def loadFromStream(self, inputStream, lineNumber, verified):
    while True:
      lineNumber += 1
      line = inputStream.readline()
      if len(line)==0:  # eof
        return -1
      line = line.rstrip('\n')
      if line == '':
        self._elaborateGraphStructure()
        return lineNumber
      elif line[0] == '#':
        self._comments.append(line)
        if re.match('^# sent_id = .+',line):
          self._sentID = line[12:]
      # default handles MWTs cleanly also
      else:
        self._tokens.append(self._factory.createToken(lineNumber, line))
        if not re.match('[0-9]+-',line):
          currIndex = len(self._tokens)-1
          udIndex = self._tokens[currIndex]['index']
          self._index2index[udIndex] = currIndex
          if lineNumber in verified:
            self._tokens[currIndex].addVerified(verified[lineNumber])

  def conlluString(self):
    return '\n'.join(self._comments) + '\n' + '\n'.join(t.conlluString() for t in self._tokens if not t.isRoot()) + '\n'

  def reportString(self):
    ans = ''
    for t in self._tokens:
      if not t.isRoot():
        oneReport = t.reportString()
        if oneReport != '':
          ans = ans + '\n' + oneReport
    return ans

  def runChecks(self, lexicon):
    for t in self._tokens:
      t.runChecks(lexicon)

  def _elaborateGraphStructure(self):
    pred = self._tokens[0]
    # start at 1 to skip root token which has no head or predecessor
    for i in range(1,len(self._tokens)):
      t = self._tokens[i]
      if not t.isMultiwordToken():
        if t['head'] not in self._index2index:
          print('Problem with sentence',self._sentID)
        head = self._tokens[self._index2index[t['head']]]
        t.setHead(head)
        head.addDependent(t)
        t.setPredecessor(pred)
        pred = t

#########################################################################
# UDCorpus class                                                        #
#########################################################################

class UDCorpus:

  def __init__(self, languageCode):
    self._sentences = list()
    self._languageCode = languageCode.upper()

  def loadFromStream(self, inputStream, verified):
    lineNumber = 0
    while True:
      sentence = UDSentence(self._languageCode)
      lineNumber = sentence.loadFromStream(inputStream, lineNumber, verified)
      if lineNumber != -1:
        self._sentences.append(sentence)
      else:
        return

  def conlluString(self):
    return '\n'.join(s.conlluString() for s in self._sentences)

  def reportString(self):
    ans = ''
    for t in self._sentences:
      oneReport = t.reportString()
      if oneReport != '':
        ans = ans + '\n' + oneReport
    return ans

  def runChecks(self, dictionaryFileName=None):
    lexicon = UDDictionary(dictionaryFileName)
    for s in self._sentences:
      s.runChecks(lexicon)

  def __len__(self):
    return len(self._sentences)
