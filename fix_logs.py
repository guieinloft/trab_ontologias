import re

def fix_consultas():
    with open('consultas_sparql.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Block 1
    content = re.sub(
        r'SEPARADOR = "═" \* 78\ndef imprimir_consultas\(\) -> None:\n\tcategoria_atual = ""\n\tprint\(f"\\n\{\'╔\' \+ SEPARADOR \+ \'╗\'\}"\)\n\tprint\(f"\{\'║\'\} \{\'CONSULTAS SPARQL — ONTOLOGIA DO BANHADO DO TAIM\':\^76s\} \{\'║\'\}"\)\n\tprint\(f"\{\'║\'\} \{\'Atropelamento de Fauna Silvestre\':\^76s\} \{\'║\'\}"\)\n\tprint\(f"\{\'╚\' \+ SEPARADOR \+ \'╝\'\}\\n"\)',
        'def imprimir_consultas() -> None:\n\tcategoria_atual = ""\n\tprint("\\n--- CONSULTAS SPARQL - ONTOLOGIA DO BANHADO DO TAIM ---")',
        content
    )

    # Block 2
    content = re.sub(
        r'print\(f"\\n\{\'▓\' \* 78\}"\)\n\t\t\tprint\(f"  CATEGORIA: \{categoria_atual\.upper\(\)\}"\)\n\t\t\tprint\(f"\{\'▓\' \* 78\}\\n"\)',
        'print(f"\\n### CATEGORIA: {categoria_atual.upper()} ###")',
        content
    )

    # Block 3
    content = re.sub(
        r'print\(f"\{\'─\' \* 78\}"\)\n\t\tprint\(f"  \[\{q\.codigo\}\] \{q\.titulo\}"\)\n\t\tprint\(f"\{\'─\' \* 78\}"\)',
        'print(f"\\n[{q.codigo}] {q.titulo}")',
        content
    )

    # Block 4
    content = re.sub(
        r'print\("\\n  \[!\] rdflib não instalado\. Instale com: pip install rdflib"\)\n\t\tprint\("\t  As consultas foram impressas acima para execução manual\.\\n"\)',
        'print("\\n[!] rdflib nao instalado. As consultas foram impressas acima para execucao manual.")',
        content
    )

    # Block 5
    content = re.sub(
        r'print\(f"\\n\{\'╔\' \+ SEPARADOR \+ \'╗\'\}"\)\n\tprint\(f"\{\'║\'\} \{\'EXECUÇÃO DAS CONSULTAS VIA RDFLIB\':\^76s\} \{\'║\'\}"\)\n\tprint\(f"\{\'╚\' \+ SEPARADOR \+ \'╝\'\}\\n"\)',
        'print("\\n--- EXECUCAO DAS CONSULTAS VIA RDFLIB ---")',
        content
    )
    
    # Block 6: Error/Success symbols
    content = content.replace('print(f"  ✓ Ontologia carregada: {owl_path}")', 'print(f"  [OK] Ontologia carregada: {owl_path}")')
    content = content.replace('print(f"  ✗ Erro ao carregar {owl_path}: {e}")', 'print(f"  [X] Erro ao carregar {owl_path}: {e}")')
    content = content.replace('print(f"  ✗ Erro na execução: {e}")', 'print(f"  [X] Erro na execucao: {e}")')
    content = content.replace('print(f"  → {len(linhas)} resultado(s):\\n")', 'print(f"  -> {len(linhas)} resultado(s):")')
    content = content.replace('print(f"\t{\' │ \'.join(valores)}")', 'print(f"\t{\' | \'.join(valores)}")')
    content = content.replace('print("  → 0 resultados (conjunto vazio)")', 'print("  -> 0 resultados")')
    
    # Also replace general unicode
    content = content.replace('DESCRIÇÃO', 'DESCRICAO')
    content = content.replace('CÓDIGO SPARQL', 'CODIGO SPARQL')
    content = content.replace('EXECUÇÃO', 'EXECUCAO')
    content = content.replace('—', '-')

    with open('consultas_sparql.py', 'w', encoding='utf-8') as f:
        f.write(content)

def fix_extracao():
    with open('extracao_conhecimento.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Block 1
    content = re.sub(
        r'print\("\\n" \+ "=" \* 70\)\n\t\tprint\("  RESUMO DA EXTRAÇÃO DE CONHECIMENTO"\)\n\t\tprint\("=" \* 70\)',
        'print("\\n--- RESUMO DA EXTRACAO DE CONHECIMENTO ---")',
        content
    )
    
    # Block 2
    content = re.sub(
        r'print\(f"\\n  ENTIDADES EXTRAÍDAS: \{len\(entidades\)\}"\)\n\t\tprint\("  " \+ "-" \* 40\)',
        'print(f"\\nENTIDADES EXTRAIDAS: {len(entidades)}")',
        content
    )

    # Block 3
    content = re.sub(
        r'barra = "█" \* min\(n, 30\)\n\t\t\tprint\(f"\t\{cls:<28s\} \{n:>4d\}  \{barra\}"\)',
        'print(f"\t{cls:<28s} {n:>4d}")',
        content
    )

    # Block 4
    content = re.sub(
        r'print\(f"\\n  TRIPLAS EXTRAÍDAS: \{len\(triplas\)\}"\)\n\t\tprint\("  " \+ "-" \* 40\)\n\t\tprint\("  Por relação ontológica:"\)',
        'print(f"\\nTRIPLAS EXTRAIDAS: {len(triplas)}\\nPor relacao ontologica:")',
        content
    )

    # Block 5
    content = re.sub(
        r'print\("\\n  Por método de extração:"\)',
        'print("\\nPor metodo de extracao:")',
        content
    )

    # Block 6
    content = re.sub(
        r'print\(f"\\n  EXEMPLOS DE TRIPLAS \(primeiras 15\):"\)\n\t\tprint\("  " \+ "-" \* 40\)',
        'print(f"\\nEXEMPLOS DE TRIPLAS (primeiras 15):")',
        content
    )

    # Block 7
    content = re.sub(
        r'print\("\\n" \+ "=" \* 70\)',
        'print("\\n--- FIM ---")',
        content
    )

    with open('extracao_conhecimento.py', 'w', encoding='utf-8') as f:
        f.write(content)

fix_consultas()
fix_extracao()
print("Done")
