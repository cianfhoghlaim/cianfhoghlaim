import os
import re

def patch_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # 1. Fix function arguments: 'word string' -> 'word: string'
    # Match: function Name(\n  word string
    def fix_args(match):
        args_block = match.group(1)
        # Fix lines like: word string @description("...")
        fixed_args = re.sub(r'^\s*([a-zA-Z_0-9]+)\s+([a-zA-Z_0-9\[\]\<\>]+(\?)?)\s*(@description|)', r'  \1: \2 \4', args_block, flags=re.MULTILINE)
        return f"function {match.group(0).split('(')[0].split()[-1]}({fixed_args}"
        
    # We just need to fix function definitions.
    # A simpler way: Find all function declarations and replace the parameters inside them.
    functions = re.finditer(r'function\s+[A-Za-z0-9_]+\s*\((.*?)\)\s*->', content, re.DOTALL)
    for func in functions:
        orig_args = func.group(1)
        # Replace 'param type' with 'param: type'
        # Be careful not to replace things that already have colons
        new_args = re.sub(r'^\s*([a-zA-Z0-9_]+)\s+([a-zA-Z0-9_\[\]\?\<\>]+)(.*?)$', r'  \1: \2\3', orig_args, flags=re.MULTILINE)
        content = content.replace(orig_args, new_args)

    # 2. Fix the duplicate enum PartOfSpeech in tearma.baml
    if "tearma.baml" in filepath:
        content = content.replace("enum PartOfSpeech {", "enum TearmaPartOfSpeech {")
        content = content.replace("part_of_speech: PartOfSpeech", "part_of_speech: TearmaPartOfSpeech")
        content = content.replace("part_of_speech PartOfSpeech", "part_of_speech: TearmaPartOfSpeech")

    with open(filepath, 'w') as f:
        f.write(content)

for root, _, files in os.walk('oideachais/baml_src'):
    for file in files:
        if file.endswith('.baml'):
            patch_file(os.path.join(root, file))

