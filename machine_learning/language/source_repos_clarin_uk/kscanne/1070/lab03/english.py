import math
dialects = ['en-AU', 'en-BW', 'en-CA', 'en-GB', 'en-HK', 'en-IE', 'en-IN', 'en-JM', 'en-KE', 'en-NG', 'en-NZ', 'en-PH', 'en-SG', 'en-TT', 'en-US', 'en-ZA']
table = dict()

def showprobs(w):
  entropy = 0.0
  probsum = 0.0
  for d in dialects:
    if w in table[d]:
      probsum += table[d][w]
  for d in dialects:
    if w in table[d]:
      p=table[d][w]
      p2=p/probsum  # P(d|w)
      print 'P('+w+'|'+d+')='+str(p)
      entropy -= p2*math.log(p2,2)
    else:
      print 'P('+w+'|'+d+')=0.0'
  print 'Entropy='+str(entropy)
  print

# read each frequency list
for d in dialects:
  table[d] = dict()
  freqfile = file(d + '.txt')
  total = 0
  for line in freqfile:
    line = line.rstrip('\n')
    pieces = line.split(',')
    count = int(pieces[1])
    table[d][pieces[0]] = count
    total += count
  freqfile.close()
  # convert counts into probabilities
  for w in table[d]:
    table[d][w] = table[d][w] / float(total)

showprobs('the')
showprobs('of')
showprobs('and')

# From the code above, you can get P(w|d) as table[d][w]
S = ['Soccer','is','my','favourite','sport']
