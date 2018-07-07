import argparse
from os.path import dirname, join, basename
from cmdparser import Parser
from code import Code


code = Code()
st = {'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3, 'R4': 4, 'R5': 5, 'R6': 6, 'R7': 7,
      'R8': 8, 'R9': 9, 'R10': 10, 'R11': 11, 'R12': 12, 'R13': 13, 'R14': 14,
      'R15': 15, 'SCREEN': 16384, 'KBD': 24576, 'SP': 0, 'LCL': 1, 'ARG': 2,
      'THIS': 3, 'THAT': 4, 'WRITE': 18, 'END': 22}

parser = argparse.ArgumentParser(description='assembly language to binary')
parser.add_argument('asm')
arg = parser.parse_args()

with open(arg.asm, 'r') as sc:
    lines = sc.readlines()

cleaned = []
# clean up the whitespace and comments
for line in lines:
    line = line.split('//')[0].strip()
    if line:
        cleaned.append(line)

# first pass: find and add all labels
line_num = 0
code_lines = []
for (i, line) in enumerate(cleaned):
    if line.startswith('('):
        st[line[1:-1]] = line_num
        continue
    code_lines.append(i)
    line_num += 1

# second pass: process each line of command
translated = []
n = 16  # first available RAM address
for i in code_lines:
    if not cleaned[i].startswith('@'):
        parser = Parser(cleaned[i])
        d = code.dest(parser.dest())
        c = code.comp(parser.comp())
        j = code.jump(parser.jump())
        translated.append('111' + c + d + j)
    else:
        try:
            addr = int(cleaned[i][1:])
            translated.append(code.addr(addr))
        except ValueError:
            if cleaned[i][1:] in st:
                translated.append(code.addr(st[cleaned[i][1:]]))
            else:
                st[cleaned[i][1:]] = n
                translated.append(code.addr(st[cleaned[i][1:]]))
                n += 1

hack_output = join(dirname(arg.asm),
                   basename(arg.asm).split('.')[0] + '.hack')
with open(hack_output, 'w') as output:
    for line in translated:
        output.write('{}\n'.format(line))
