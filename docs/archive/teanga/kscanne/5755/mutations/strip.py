import re
import sys
import io

def strip_mutation(tok):
  if re.match('bhf', tok):
    return ('U',re.sub('^bh','',tok))
  elif re.match('[a-záéíóú]h', tok):
    return ('S',re.sub('^(.)h',r'\1',tok))
  elif re.match('h-?[a-záéíóú]', tok):
    return ('H',re.sub('^h-?','',tok))
  elif re.match('t[s-][a-záéíóú]', tok):
    return ('T',re.sub('^t-?','',tok))
  elif re.match('n-[a-záéíóú]', tok):
    return ('U',re.sub('^n-','',tok))
  elif re.match('(mb|gc|n[dg]|bp|dt)', tok):
    return ('U',re.sub('^.','',tok))
  else:
    return ('N',tok)

if __name__ == '__main__':
  input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
  for line in input_stream:
    (m,w) = strip_mutation(line.rstrip('\n'))
    print(w+"\t"+m)
