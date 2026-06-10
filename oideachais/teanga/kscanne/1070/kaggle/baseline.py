#coding: utf-8
import random, re, codecs
random.seed()

# returns random 0 or 1
def coin_flip():
  return random.randint(0,1)

print 'id,label'
with codecs.open('test.tsv', 'r', 'utf-8') as f:
  patt = re.compile(ur"[A-ZÁÉÍÓÚa-záéíóú'-]+", re.UNICODE)
  for row in f:
    pieces = row.split("\t")
    sentence_id = pieces[0]
    sentence = pieces[1]
    sentence_len = len(sentence)
    sentence_words = re.findall(patt, sentence)  # list of words
    word_count = len(sentence_words)
    # put your rule here; this example labels the sentence as News
    # if it contains the Irish word for "news", upper or lowercase,
    # and just flips a coin if it doesn't
    if 'nuacht' in sentence_words or 'Nuacht' in sentence_words:
      label = 0
    else:
      label = coin_flip()
    print sentence_id+','+str(label)
