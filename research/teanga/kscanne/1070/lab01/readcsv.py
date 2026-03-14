import csv

with open('tweets.csv', 'rb') as f:
  reader = csv.DictReader(f, delimiter=',')
  for row in reader:
    lati = float(row['latitude'])
    longi = float(row['longitude'])
    count = int(row['tweets'])
    if count > 0:
      print lati, longi
