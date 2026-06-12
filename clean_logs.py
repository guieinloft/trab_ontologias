import re

with open("extracao_conhecimento.py", "r", encoding="utf-8") as f:
    content = f.read()

# Simplify basic config
content = content.replace(
    'format="%(asctime)s │ %(levelname)-8s │ %(message)s",',
    'format="%(asctime)s - %(levelname)s - %(message)s",'
)

# Global replacements for characters
replacements = {
    "✓": "OK",
    "✗": "ERRO",
    "⚠": "AVISO",
    "—": "-",
    "█": "*",
    "╔": "+",
    "═": "-",
    "╗": "+",
    "║": "|",
    "╚": "+",
    "╝": "+"
}
for k, v in replacements.items():
    content = content.replace(k, v)

# Simplify block headers
content = content.replace(
    'logger.info("\\n" + "=" * 65)\n\t\tlogger.info("  ETAPA 1: COLETA DE FONTES (MULTIMODAL)")\n\t\tlogger.info("=" * 65)',
    'logger.info("=== ETAPA 1: COLETA DE FONTES (MULTIMODAL) ===")'
)

content = content.replace(
    'logger.info("=" * 65)\n\t\tlogger.info("  ETAPA 2: INICIALIZAÇÃO DO PIPELINE NLP")\n\t\tlogger.info("=" * 65)',
    'logger.info("=== ETAPA 2: INICIALIZACAO DO PIPELINE NLP ===")'
)

content = content.replace(
    'print("\\n" + "=" * 70)\n\t\tprint("  RESUMO DA EXTRAÇÃO DE CONHECIMENTO")\n\t\tprint("=" * 70)',
    'print("\\n=== RESUMO DA EXTRACAO DE CONHECIMENTO ===")'
)

content = content.replace(
    'logger.info("+" + "-" * 63 + "+")\n\tlogger.info("|  EXTRAÇÃO DE CONHECIMENTO - BANHADO DO TAIM			  |")\n\tlogger.info("|  Domínio: Atropelamento de Fauna Silvestre			   |")\n\tlogger.info("+" + "-" * 63 + "+")',
    'logger.info("=== EXTRACAO DE CONHECIMENTO - BANHADO DO TAIM ===")'
)

content = content.replace(
    'logger.info("\\n" + "=" * 65)\n\tlogger.info("  ETAPA 3: EXTRAÇÃO DE ENTIDADES E RELAÇÕES")\n\tlogger.info("=" * 65)',
    'logger.info("=== ETAPA 3: EXTRACAO DE ENTIDADES E RELACOES ===")'
)

content = content.replace(
    'logger.info("\\n" + "=" * 65)\n\tlogger.info("  ETAPA 4: CONSOLIDAÇÃO E EXPORTAÇÃO")\n\tlogger.info("=" * 65)',
    'logger.info("=== ETAPA 4: CONSOLIDACAO E EXPORTACAO ===")'
)

content = content.replace(
    'print("  " + "-" * 40)',
    'print("  ----------------------------------------")'
)

with open("extracao_conhecimento.py", "w", encoding="utf-8") as f:
    f.write(content)

# consultas_sparql.py
with open("consultas_sparql.py", "r", encoding="utf-8") as f:
    content = f.read()

for k, v in replacements.items():
    content = content.replace(k, v)

content = content.replace("▓", "#")
content = content.replace("─", "-")
content = content.replace(" │ ", " | ")

content = re.sub(
    r'print\(f"\\n\{\'\+\' \+ SEPARADOR \+ \'\+\'\}\"\)\n\tprint\(f"\{\'\|\'\} \{\'CONSULTAS SPARQL - ONTOLOGIA DO BANHADO DO TAIM\':\^76s\} \{\'\|\'\}\"\)\n\tprint\(f"\{\'\|\'\} \{\'Atropelamento de Fauna Silvestre\':\^76s\} \{\'\|\'\}\"\)\n\tprint\(f"\{\'\+\' \+ SEPARADOR \+ \'\+\'\}\\n\"\)',
    r'print("\\n=== CONSULTAS SPARQL - ONTOLOGIA DO BANHADO DO TAIM ===")',
    content
)

content = re.sub(
    r'print\(f"\\n\{\'\#\' \* 78\}\"\)\n\t\t\tprint\(f"  CATEGORIA: \{categoria_atual\.upper\(\)\}"\)\n\t\t\tprint\(f"\{\'\#\' \* 78\}\\n\"\)',
    r'print(f"\\n### CATEGORIA: {categoria_atual.upper()} ###")',
    content
)

content = re.sub(
    r'print\(f"\{\'\-\' \* 78\}\"\)\n\t\tprint\(f"  \[\{q\.codigo\}\] \{q\.titulo\}"\)\n\t\tprint\(f"\{\'\-\' \* 78\}\"\)',
    r'print(f"\\n[{q.codigo}] {q.titulo}")',
    content
)

content = re.sub(
    r'print\(f"\\n\{\'\+\' \+ SEPARADOR \+ \'\+\'\}\"\)\n\tprint\(f"\{\'\|\'\} \{\'EXECUÇÃO DAS CONSULTAS VIA RDFLIB\':\^76s\} \{\'\|\'\}\"\)\n\tprint\(f"\{\'\+\' \+ SEPARADOR \+ \'\+\'\}\\n\"\)',
    r'print("\\n=== EXECUCAO DAS CONSULTAS VIA RDFLIB ===")',
    content
)

with open("consultas_sparql.py", "w", encoding="utf-8") as f:
    f.write(content)
