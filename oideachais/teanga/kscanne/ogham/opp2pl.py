from lark import Lark
import sys
sys.stdin.reconfigure(encoding='utf-8')

def translate(t):
  if t.data == 'start':
    return ''.join(map(translate, t.children))
  elif t.data == 'halt':
    return 'print "@r\\n";exit(0);'
  elif t.data[0:3] == 'inc':
    return '$r['+str(int(t.data[3])-1)+']++;'
  elif t.data[0:3] == 'dec':
    return '$r['+str(int(t.data[3])-1)+']--;'
  elif t.data[0:4] == 'loop':
    return 'while($r['+str(int(t.data[4])-1)+']){' + ''.join(map(translate, t.children)) + '}'
  else:
    raise SyntaxError("bad tree")

with open('ogham.lark', 'r', encoding="utf-8") as f:
  my_grammar = f.read()
parser = Lark(my_grammar)
program = sys.stdin.read()
parse_tree = parser.parse(program)
print('@r=(0,0,0,0,0);'+translate(parse_tree))
