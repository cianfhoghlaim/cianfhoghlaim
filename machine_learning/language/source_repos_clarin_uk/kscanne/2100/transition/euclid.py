def gcd(u,v):
  # Euclid's algorithm
  while v != 0:
    r = u % v
    u = v
    v = r
  return u

if __name__ == '__main__':
  a = int(raw_input('First value: '))
  b = int(raw_input('Second value: '))
  print 'gcd:', gcd(a,b)
