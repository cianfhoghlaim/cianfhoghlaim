import csv
import math

k = 1
traincount = 500

def distance(v1,v2):
  ans = 0
  for i in range(1,len(v1)):   # index 0 is the label...
    ans += pow(abs(v1[i] - v2[i]),2)
  return math.sqrt(ans)

trainingdata = list()
with open('train.csv', 'rb') as f:
  reader = csv.reader(f, delimiter=',')
  for row in reader:
    if len(trainingdata) < traincount:
      trainingdata.append([int(x) for x in row])

tested=0
correct=0
confusion=dict()
with open('test.csv', 'rb') as f:
  reader = csv.reader(f, delimiter=',')
  for row in reader:
    totest = [int(x) for x in row]
    distances=dict()
    for i in range(len(trainingdata)):
      distances[i] = distance(totest, trainingdata[i])
    votes=dict()
    for i in range(10):
      votes[i] = 0
    for nbr in sorted(distances, key=distances.get)[0:k]:
      votes[trainingdata[nbr][0]] += 1
    guess = sorted(votes, key=votes.get, reverse=True)[0]
    both=str(totest[0])+','+str(guess)
    print 'guess,correct = '+both
    if both in confusion:
      confusion[both] += 1
    else:
      confusion[both] = 1
    if totest[0] == guess:
      correct += 1
    tested += 1

percent = (100.0*correct)/tested
print str(correct) + ' correct out of ' + str(tested) + ", " + str(percent) + '%'

print 'Confusion matrix:'
print '   0  1  2  3  4  5  6  7  8  9'
for j in range(10):
  rowstr=str(j)
  for k in range(10):
    key=str(j)+','+str(k)
    if key in confusion:
      rowstr += '{:>3}'.format(str(confusion[key]))
    else:
      rowstr += '  0'
  print rowstr
