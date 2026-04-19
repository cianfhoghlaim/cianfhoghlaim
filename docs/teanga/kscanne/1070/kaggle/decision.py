#coding: utf-8
import random, re, codecs
random.seed()

# returns random 0 or 1
def coin_flip():
  return random.randint(0,1)

decision_list = []
with codecs.open('bestwords.txt', 'r', 'utf-8') as f:
  for line in f:
    line = line.rstrip('\n')
    decision_list.append(line.split(','))

print 'id,label'
with codecs.open('test.tsv', 'r', 'utf-8') as f:
  patt = re.compile(ur"[A-ZÁÉÍÓÚa-záéíóú'-]+", re.UNICODE)
  for row in f:
    pieces = row.split("\t")
    sentence_id = pieces[0]
    sentence = pieces[1].lower()
    sentence_len = len(sentence)
    sentence_words = re.findall(patt, sentence)  # list of words
    word_count = len(sentence_words)
    label = str(coin_flip())
    for pair in decision_list:
      if pair[0] in sentence_words:
        label = pair[1]
        break
    print sentence_id+','+label
