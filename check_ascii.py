import re

def check_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        if 'print' in line:
            # check if line has non-ascii
            non_ascii = [c for c in line if ord(c) > 127]
            if non_ascii:
                print(f"{filename}:{i+1}: {line.strip()} -> Non-ASCII: {set(non_ascii)}")

check_file('consultas_sparql.py')
check_file('extracao_conhecimento.py')
