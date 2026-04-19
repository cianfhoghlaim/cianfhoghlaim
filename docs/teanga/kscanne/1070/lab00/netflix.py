csvfile = file('ratings-training.csv')
ratings = []
for row in csvfile:
  oneuser = row.rstrip().split(',')
  ratings.append(oneuser)


total=0     # sum of all the ratings in the row
count=0.0   # number of real (not ? or -) ratings in the row
for c in range(30):
  x = ratings[11][c]
  if x != '?' and x != '-':
    total = total + int(x)
    count = count + 1

print total/count
