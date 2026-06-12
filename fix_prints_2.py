import re

with open('consultas_sparql.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the line ─ block
content = re.sub(
    r'print\(f"\\n\{\'─\' \* 78\}"\)\n\t\tprint\(f"  \[\{q\.codigo\}\] \{q\.titulo\}"\)\n\t\tprint\(f"\{\'─\' \* 78\}"\)',
    'print(f"\\n[{q.codigo}] {q.titulo}")',
    content
)

# Any remaining ─
content = content.replace("─", "-")

# Replace accents in print
content = content.replace('print(f"\\n  Execução concluída. {len(CONSULTAS)} consultas processadas.\\n")', 'print(f"\\n  Execucao concluida. {len(CONSULTAS)} consultas processadas.\\n")')
content = content.replace('print("\\n  [i] Arquivo ontologia_taim.owl não encontrado.")', 'print("\\n  [i] Arquivo ontologia_taim.owl nao encontrado.")')
content = content.replace('print("\\t  Execute ontologia_taim.py primeiro para gerá-lo.\\n")', 'print("\\t  Execute ontologia_taim.py primeiro para gera-lo.\\n")')

with open('consultas_sparql.py', 'w', encoding='utf-8') as f:
    f.write(content)
