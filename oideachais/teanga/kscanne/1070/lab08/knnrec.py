import csv
import math

k = 3

def dot(v1,v2):
  ans = 0
  for i in range(len(v1)):
    if v1[i] != '?' and v1[i] != '-' and v2[i] != '?' and v2[i] != '-':
      ans += float(v1[i])*float(v2[i])
  return ans

def magnitude(v1):
  return math.sqrt(dot(v1,v1))

def cosine_similarity(v1,v2):
  return dot(v1,v2)/(magnitude(v1)*magnitude(v2))

users = list()
with open('ratings-training.csv', 'rb') as f:
  reader = csv.reader(f, delimiter=',')
  for row in reader:
    users.append(row)

def best_guess(user_index, movie_index, verbose=True):
  similarities=dict()
  for i in range(len(users)):
    if i != user_index:
      similarities[i] = cosine_similarity(users[user_index], users[i])
  total_sim = 0.0
  prediction = 0.0
  for nbr in sorted(similarities, key=similarities.get, reverse=True)[0:k]:
    rating = users[nbr][movie_index]
    if verbose:
      print 'user at index ' + str(nbr) + ' is a near nbr, sim = ' + str(similarities[nbr]) + ', rating=' + rating
    if rating != '?' and rating != '-':
      prediction += float(users[nbr][movie_index])*similarities[nbr]
      total_sim += similarities[nbr]
  if total_sim == 0.0:
    return '-'
  else:
    return prediction / total_sim;

def get_missing():
  for i in range(len(users)):
    movie_to_guess = users[i].index('?')
    print int(round(best_guess(i,movie_to_guess,False)))

if __name__ == "__main__":
  get_missing()
