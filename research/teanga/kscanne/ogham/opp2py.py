from lark import Lark
import sys
sys.stdin.reconfigure(encoding='utf-8')

def translate(t, indent):
  ind = (' '*indent)
  if t.data == 'start':
    return '\n'.join(map(lambda c: translate(c,indent), t.children))
  elif t.data == 'halt':
    return ind+"print(' '.join([str(x) for x in r]))\n"+ind+"exit(0)" 
  elif t.data[0:3] == 'inc':
    return ind+'r['+str(int(t.data[3])-1)+']+=1'
  elif t.data[0:3] == 'dec':
    return ind+'r['+str(int(t.data[3])-1)+']-=1'
  elif t.data[0:4] == 'loop':
    return ind+'while r['+str(int(t.data[4])-1)+']!=0:\n'+'\n'.join(map(lambda c: translate(c,indent+2), t.children))
  else:
    raise SyntaxError("bad tree")

with open('ogham.lark', 'r', encoding="utf-8") as f:
  my_grammar = f.read()
parser = Lark(my_grammar)
program = sys.stdin.read()
parse_tree = parser.parse(program)
print('r=[0,0,0,0,0]\n'+translate(parse_tree,0))
