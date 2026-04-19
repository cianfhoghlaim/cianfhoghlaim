import sys
import os
from ud import UDCorpus

def printUsage():
  print("Usage: python3 main.py [ga|gd|gv] [-r] [input-conllu-file]")
  print("       Use option -r to output a report of potential issues.")
  print("       Otherwise, a modified CONLLU file is output.")

def loadSicFile(conlluFilename):
  answer = dict()
  if conlluFilename!='<stdin>':
    sicFileName = os.path.basename(conlluFilename).replace('.conllu','.sic')
    try:
      sicFile = open('sic/'+sicFileName)
      for line in sicFile:
        lineNum, feat = line.rstrip('\n').split('\t')
        lineNum = int(lineNum)
        if lineNum not in answer:
          answer[lineNum] = dict()
        answer[lineNum][feat] = 1
    except IOError:
      pass  # no big deal if there's no .sic file
  return answer

lexicons = {
  'ga': '/home/kps/gaeilge/parsail/treebank/tagdict.tsv',
  'gd': '/home/kps/gaeilge/ga2gd/ga2gd/ud/tagdict.tsv',
  'gv': '/home/kps/gaeilge/ga2gv/ga2gv/ud/tagdict.tsv'
}

if len(sys.argv)<2 or len(sys.argv)>4 or sys.argv[1] not in lexicons:
  printUsage()
  sys.exit(1)

outputReport = False
inputStream = sys.stdin
languageCode = sys.argv[1]
if len(sys.argv)>2:
  if sys.argv[2]=='-r':
    outputReport = True
    sys.argv.pop(2)
if len(sys.argv)>2:
  try:
    inputStream = open(sys.argv[2])
  except IOError:
    print("Failed to read input file", sys.argv[2])
    sys.exit(1)

c = UDCorpus(languageCode)
c.loadFromStream(inputStream, loadSicFile(inputStream.name))
if inputStream is not sys.stdin:
  inputStream.close()

#c.runChecks(lexicons[languageCode])
c.runChecks()

if outputReport:
  print(c.reportString())
else:
  print(c.conlluString())
