#coding: utf-8
import re, codecs, sys, math
reload(sys)
sys.setdefaultencoding('utf-8')

### tweakable stuff!!! ###

# regular expression for defining what a "word" is
patt = re.compile(ur"[A-ZÁÉÍÓÚa-záéíóú'-]+", re.UNICODE)
# a bit like the "add-alpha" smoothing we talked about
smoothing = 0.5
# ignore words that appear fewer than this number of times total
prune = 3
# output this number of low-entropy words
keep = 50

freqs = dict()  # freqs['agus'][0] = 234728  or whatever
totals = [0,0]  # total number of training sentences in each class

# pass list of counts
def entropy(counts):
  tot = float(sum(counts))
  probs = [c/tot for c in counts]
  ans = 0.0
  for p in probs:
    if p > 0:
      ans -= p*math.log(p,2)
  return ans

def read_training(fname, classnum):
  with codecs.open(fname, 'r', 'utf-8') as f:
    for sentence in f:
      totals[classnum] += 1
      sentence_words = re.findall(patt, sentence)
      unique = [x.lower() for x in set(sentence_words)]
      for w in unique:
        if w not in freqs:
          freqs[w] = [smoothing,smoothing]
        freqs[w][classnum] += 1

read_training('news.txt',0)
read_training('science.txt',1)

# compute an entropy score for each word
score = dict()
for w in freqs:
  total_training = sum(totals)
  total_times_w_seen = sum(freqs[w])
  if total_times_w_seen >= prune:
    w_prior = total_times_w_seen / float(total_training)
    without_freqs = [totals[i] - freqs[w][i] for i in range(2)]
    score[w] = entropy(freqs[w])
    # or weight by frequency as we did with out decision tree algorithm: 
    # score[w] = w_prior*entropy(freqs[w]) + (1 - w_prior)*entropy(without_freqs)

count = 0
# output words from smallest (best) entropy to highest (worst)
for w in sorted(score, key=score.get):
  label = 0
  if freqs[w][1] > freqs[w][0]:
    label = 1
  print w.encode('utf-8') + "," + str(label)
  count += 1
  if count == keep:
    break
