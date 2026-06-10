from lark import Lark
import sys
sys.stdin.reconfigure(encoding='utf-8')

def translate(t):
  if t.data == 'start':
    return ''.join(map(translate, t.children))
  elif t.data == 'halt':
    return ''
  elif t.data[0:3] == 'inc':
    index = int(t.data[3])-1
    return ('>'*index)+'+'+('<'*index)
  elif t.data[0:3] == 'dec':
    index = int(t.data[3])-1
    return ('>'*index)+'-'+('<'*index)
  elif t.data[0:4] == 'loop':
    index = int(t.data[4])-1
    moveto = '>'*index
    goback = '<'*index
    return moveto+'['+goback+''.join(map(translate, t.children))+moveto+']'+goback
  else:
    raise SyntaxError("bad tree")

with open('ogham.lark', 'r', encoding="utf-8") as f:
  my_grammar = f.read()
parser = Lark(my_grammar)
program = sys.stdin.read()
parse_tree = parser.parse(program)
print(translate(parse_tree))
