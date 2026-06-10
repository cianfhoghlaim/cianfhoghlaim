import sys
import re

slenderVowels = 'eéEÉiíIÍ'
broadVowels = 'aáAÁoóOÓuúUÚ'

def hasSlenderInitial(w):
  for c in w:
    if c in slenderVowels:
      return True
    if c in broadVowels:
      return False
  return False

def hasBroadInitial(w):
  for c in w:
    if c in slenderVowels:
      return False
    if c in broadVowels:
      return True
  return False

# pass something like Clétó and it return Cléató
# or pass Dámacléas and it returns Dámaicléas
def caollecaol(w):
  ans = ''
  currBroad = False
  lastVowel = False
  for i in range(len(w)):
    if w[i] in slenderVowels:
      currBroad = False
      lastVowel = True
    elif w[i] in broadVowels:
      currBroad = True
      lastVowel = True
    else:
      if lastVowel:
        if hasSlenderInitial(w[i:]) and currBroad or w[i-1] in 'éÉeE':
          ans += 'i'
        elif hasBroadInitial(w[i:]) and not currBroad:
          ans += 'a'   # TODO: broaden i/í with o? or leave this and add e?
      lastVowel = False
    ans += w[i] 
  return ans

def trivialTranslate(w, focloir):
  ans = ''
  for c in w:
    if c in focloir:
      ans += focloir[c]
    elif c in '\u0301\u0313':
      pass
    else:
      if c.lower() in focloir:
        ans += focloir[c.lower()].upper()
      else:
        ans += c
  return ans

def dedouble(w):
  w = re.sub('cc','c',w)
  w = re.sub('mm','m',w)
  w = re.sub('pp','p',w)
  w = re.sub('ss','s',w)
  w = re.sub('tt','t',w)
  return w

def grc2ga(w, focloir):
  w = re.sub('αο','á',w)
  w = re.sub('έα','é',w)
  w = re.sub('οά','ó',w)
  w = re.sub('[ηῆ]ς','éas',w)
  w = re.sub('εύς','éas',w)
  w = re.sub('ε[υύ]','eo',w)
  w = re.sub('ου','ú',w)
  w = re.sub('αί','ae',w)
  w = re.sub('ία$','ia',w)
  w = re.sub('α$','e',w)
  w = trivialTranslate(w, focloir)
  w = caollecaol(w)
  w = dedouble(w)
  return w

mapper = dict()
with open('map.tsv', 'r', encoding="utf-8") as f:
  for line in f:
    line = line.rstrip()
    greek, irish = line.split('\t')
    mapper[greek] = irish

for line in sys.stdin:
  line = line.rstrip()
  print(grc2ga(line, mapper))
