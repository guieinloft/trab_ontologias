import csv
import re
import os
import random
import unicodedata
from owlready2 import *
def sanitize_iri(name: str) -> str:
	n = ''.join(c for c in unicodedata.normalize('NFD', name)
				  if unicodedata.category(c) != 'Mn')
	n = re.sub(r'[^a-zA-Z0-9]', '_', n)
	n = re.sub(r'_+', '_', n)
	return n.strip('_')
def povoar_ontologia():
	onto_path = "ontologia_taim.owl"
	if not os.path.exists(onto_path):
		print(f"Erro: Arquivo '{onto_path}' não encontrado.")
		print("Execute 'python gerar_ontologia.py' primeiro para criar a TBox.")
		return
		
	onto = get_ontology("file://" + os.path.abspath(onto_path)).load()
	
	with onto:
		csv_path = "resultados_extracao/triplas_extraidas.csv"
		individuos_dict = {}
		
		def get_or_create_ind(nome, class_name):
			if not nome or not class_name: return None
			iri = sanitize_iri(nome)
			if iri == class_name:
				iri = f"{iri}_ind"
				
			if iri not in individuos_dict:
				cls = getattr(onto, class_name, None)
				if cls:
					ind = cls(iri)
					individuos_dict[iri] = ind
				else:
					return None
			return individuos_dict[iri]
		if os.path.exists(csv_path):
			with open(csv_path, "r", encoding="utf-8") as f:
				reader = csv.DictReader(f)
				for row in reader:
					e1_name = row.get("entidade1", "").strip()
					e2_name = row.get("entidade2", "").strip()
					c1_name = row.get("classe_entidade1", "").strip()
					c2_name = row.get("classe_entidade2", "").strip()
					prop_name = row.get("propriedade_ontologia", "").strip()
					ind1 = get_or_create_ind(e1_name, c1_name)
					ind2 = get_or_create_ind(e2_name, c2_name)
					if ind1 and ind2 and prop_name:
						prop = getattr(onto, prop_name, None)
						if prop:
							if issubclass(prop, FunctionalProperty):
								setattr(ind1, prop_name, ind2)
							else:
								getattr(ind1, prop_name).append(ind2)
		
		rodovia_principal = onto.Rodovia("br_471")
		
		tipos_vegetacao = [onto.TipoVegetacao(f"Vegetacao_Sintetica_{i}") for i in range(1, 11)]
		
		trechos = []
		for i in range(1, 16):
			tr = onto.TrechoRodoviario(f"Trecho_Sintetico_{i}")
			tr.atravessaHabitat.append(random.choice(tipos_vegetacao))
			trechos.append(tr)
		
		rodovia_principal.compostoPorTrechos = trechos
		mamiferos = [onto.Mamifero(f"Mamifero_Sintetico_{i}", possuiHabitat=[random.choice(tipos_vegetacao)]) for i in range(1, 31)]
		repteis = [onto.Reptil(f"Reptil_Sintetico_{i}", possuiHabitat=[random.choice(tipos_vegetacao)]) for i in range(1, 16)]
		aves = [onto.Ave(f"Ave_Sintetica_{i}", possuiHabitat=[random.choice(tipos_vegetacao)]) for i in range(1, 16)]
		
		animais = mamiferos + repteis + aves
		
		for i in range(1, 41):
			evento = onto.EventoAtropelamento(f"Evento_Atropelamento_Sintetico_{i}")
			evento.envolveAnimal.append(random.choice(animais))
			evento.ocorreEmRodovia = rodovia_principal
			evento.ocorreEmTrecho = random.choice(trechos)
	output_file = "ontologia_taim_povoada.owl"
	onto.save(output_file, format="rdfxml")
	
	print(f"Ontologia povoada salva com sucesso em '{output_file}'.")
	print("Foram criadas exatamente 125 instâncias sintéticas.")
	print(f"Indivíduos totais (Sintéticos + Extraídos): {len(list(onto.individuals()))}")
if __name__ == "__main__":
	random.seed(0)
	povoar_ontologia()

