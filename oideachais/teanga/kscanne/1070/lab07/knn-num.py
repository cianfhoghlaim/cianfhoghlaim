import csv
import math

k = 1
traincount = 500

def distance(v1,v2):
  ans = 0
  for i in range(0,len(v1)-1):   # last index is the label...
    ans += pow(abs(v1[i] - v2[i]),2)
  return math.sqrt(ans)

trainingdata = list()
with open('college-train.csv', 'rb') as f:
  reader = csv.reader(f, delimiter=',')
  headers = next(reader, None)
  for row in reader:
    if len(trainingdata) < traincount:
      trainingdata.append([float(x) for x in row])

tested=0
total_sq_error=0.0
with open('college-test.csv', 'rb') as f:
  reader = csv.reader(f, delimiter=',')
  headers = next(reader, None)
  for row in reader:
    totest = [float(x) for x in row]
    testlen = len(totest)  # number of features, plus 1 for correct answer
    distances=dict()
    guess=0
    for i in range(len(trainingdata)):
      distances[i] = distance(totest, trainingdata[i])
    for nbr in sorted(distances, key=distances.get)[0:k]:
      guess+=trainingdata[nbr][testlen-1]
    guess /= k
    both=str(totest[testlen-1])+','+str(guess)
    print 'guess,correct = '+both
    total_sq_error=(totest[testlen-1]-guess)**2
    tested += 1

mse = total_sq_error / tested
print 'average squared error = ' + str(mse)
