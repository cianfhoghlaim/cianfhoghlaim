from lark import Lark
import sys
sys.stdin.reconfigure(encoding='utf-8')

# returns a boolean "halted?"
def execute(t, env):
  if t.data == 'start':
    for child in t.children:
      if execute(child,env):
        return True
  elif t.data == 'halt':
    return True
  elif t.data[0:3] == 'inc':
    env[int(t.data[3])-1] += 1
  elif t.data[0:3] == 'dec':
    env[int(t.data[3])-1] -= 1
  elif t.data[0:4] == 'loop':
    while env[int(t.data[4])-1]!=0:
      for child in t.children:
        if execute(child,env):
          return True
  else:
    raise SyntaxError("bad tree")
  return False

with open('ogham.lark', 'r', encoding="utf-8") as f:
  my_grammar = f.read()
parser = Lark(my_grammar)
program = sys.stdin.read()
parse_tree = parser.parse(program)
mem = [0]*5
execute(parse_tree, mem)
print(' '.join([str(x) for x in mem]))
