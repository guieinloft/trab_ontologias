import re

with open('extracao_conhecimento.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if line.strip() == 'import logging':
        continue
    if 'logging.basicConfig(' in line:
        skip = True
        continue
    if skip:
        if line.strip() == ')':
            skip = False
        continue
    if 'logger = logging.getLogger(__name__)' in line:
        continue
    
    # Replace logger methods
    line = re.sub(r'logger\.(info|error|warning|debug)\(', 'print(', line)
    new_lines.append(line)

with open('extracao_conhecimento.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Replacement done.")
