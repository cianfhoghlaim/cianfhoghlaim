import math

def square(m):
  n = len(m)
  ans = []
  for i in range(n):
    ans.append([])
    for j in range(n):
      entryij = 0
      for k in range(n):
        entryij += m[i][k]*m[k][j]
      ans[i].append(entryij)
  return ans

def markovize(m):
  n = len(m)
  for j in range(n):
    colsum = 0
    for i in range(n):
      colsum += m[i][j]
    for i in range(n): 
      m[i][j] /= (1.0*colsum)

def normalize(v):
  mag = 0
  n = len(v)
  for x in v:
    mag += x*x
  mag = math.sqrt(mag)
  for i in range(n):
    v[i] /= mag

def hub_update(hubs, authorities, m):
  n = len(hubs)
  for j in range(n):
    newscore = 0
    for i in range(n):
      if m[i][j] > 0:
        newscore += authorities[i]
    hubs[j] = newscore
  normalize(hubs)
    
def auth_update(hubs, authorities, m):
  n = len(authorities)
  for i in range(n):
    newscore = 0
    for j in range(n):
      if m[i][j] > 0:
        newscore += hubs[j]
    authorities[i] = newscore
  normalize(authorities)

# columns here show outgoing edges from a given vertex, PLUS
# a 1.0 on the diagonal to allow a traveler to stay put
# This is the graph from lecture notes!
m = []
m.append([1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])
m.append([1.0,1.0,1.0,1.0,1.0,0.0,0.0,0.0])
m.append([0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0])
m.append([0.0,0.0,1.0,1.0,0.0,0.0,0.0,0.0])
m.append([0.0,0.0,0.0,0.0,1.0,1.0,0.0,0.0])
m.append([0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0])
m.append([0.0,0.0,0.0,0.0,0.0,1.0,1.0,1.0])
m.append([0.0,0.0,0.0,0.0,0.0,1.0,0.0,1.0])
markovize(m)

m2 = []
m2.append([0.7,0.2])
m2.append([0.3,0.8])

for i in range(30):
  m = square(m)

print m

h = [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]
a = [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]
for i in range(10):
  print 'Hubs: ' + str(h)
  print 'Auth: ' + str(a)
  auth_update(h,a,m)
  hub_update(h,a,m)
