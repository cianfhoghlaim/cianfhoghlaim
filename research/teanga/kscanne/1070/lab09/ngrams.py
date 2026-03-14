#coding: utf-8
import random, re, codecs, sys

def predictive_text(mod, count):
  curr = ()
  n = 1+len(random.choice(mod.keys()))
  for i in range(count):
    if len(curr) == n-1 and curr in mod:
      followers = mod[curr] 
      recs = ''
      for rec in sorted(followers, key=followers.get, reverse=True)[:3]:
        recs += ' ' + rec 
      print recs
    word = raw_input("Enter a word: ").decode(sys.stdin.encoding)
    word = word.lower()
    curr = curr + (word,)
    if len(curr) >= n:
      curr = curr[1:]

# generate a text with count tokens using the n-gram model mod
def generate(mod, count):
  random.seed()
  answer = ''
  curr = random.choice(mod.keys())  # start is an (n-1)-tuple
  for w in curr:
    answer += ' ' + w
  n = len(curr)+1
  for i in range(count-n+1):
    followers = mod[curr]
    tot = 0 
    for w in followers:
      tot += followers[w]
    choice = random.randint(1,tot)
    for w in followers:
      choice -= followers[w]
      if choice < 1:
        answer += ' ' + w
        if n>1:
          curr = curr[1:] + (w,)
        break
  return answer

def train_model(tokens,n):
  model = dict()  # keys are
  for i in range(len(tokens)-n+1):
    key = tokens[i:i+n-1]
    val = tokens[i+n-1]
    if key in model:
      if val in model[key]:
        model[key][val] += 1
      else:
        model[key][val] = 1
    else:
      model[key] = dict()
      model[key][val] = 1
  return model

def read_corpus(fn):
  answer = ()
  patt = re.compile(ur"([a-z’'-]+|[0-9]+|\S)", re.UNICODE)
  with codecs.open(fn, 'r', 'utf-8') as file:
    for line in file:
      line = line.lower()
      answer = answer + tuple(re.findall(patt, line))
  return answer

if __name__ == "__main__":
  tokens = read_corpus('README')
  train_model(tokens,3)
