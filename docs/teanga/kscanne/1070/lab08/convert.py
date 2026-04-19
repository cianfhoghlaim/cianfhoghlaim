import csv
import sys

users = dict()
movies = dict()
ratings = dict()

with open('ml-latest-small/ratings.csv', 'rb') as f:
  reader = csv.reader(f, delimiter=',')
  reader.next()   # skip header row
  for row in reader:
    userid = int(row[0])
    movieid = int(row[?])
    if movieid < ?: # only proceed if movieid < 500
      users[userid] = 1
      movies[movieid] = 1
      rating = float(row[?])
      if userid not in ratings:
        ratings[userid] = dict()
      ratings[userid][movieid] = ?

for u in users:
  rowstr = ''
  for m in movies:
    if m in ratings[u]:
      rowstr += str(ratings[?][?])+','
    else:
      rowstr += ?+','
  print rowstr[:-1]
