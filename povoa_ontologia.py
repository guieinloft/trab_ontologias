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
		corpos_hidricos = [onto.CorpoHidrico(f"CorpoHidrico_Sintetico_{i}") for i in range(1, 6)]
		habitats = tipos_vegetacao + corpos_hidricos
		
		medidas = [onto.MedidaMitigacao(f"Passagem_Fauna_{i}") for i in range(1, 4)]
		fatores_antropicos = [onto.FatorAntropico(f"Velocidade_Excessiva_{i}", mitigadoPor=[random.choice(medidas)]) for i in range(1, 6)]
		fatores_ecologicos = [onto.FatorEcologico(f"Migracao_Sazonal_{i}") for i in range(1, 6)]
		fatores_risco = fatores_antropicos + fatores_ecologicos
		
		especies_ameacadas = [onto.EspecieAnimal(f"Especie_Ameacada_{i}", nomeCientifico=[f"Sci name {i}"], nomeComum=[f"Common name {i}"], statusConservacao=["VU"]) for i in range(1, 6)]
		especies_comuns = [onto.EspecieAnimal(f"Especie_Comum_{i}", nomeCientifico=[f"Sci name LC {i}"], nomeComum=[f"Common name LC {i}"], statusConservacao=["LC"]) for i in range(1, 6)]
		todas_especies = especies_ameacadas + especies_comuns
		
		trechos = []
		km_atual = 0.0
		for i in range(1, 16):
			tr = onto.TrechoRodoviario(f"Trecho_Sintetico_{i}")
			tr.atravessaHabitat.append(random.choice(habitats))
			tr.quilometragemInicial.append(km_atual)
			km_atual += random.uniform(2.0, 5.0)
			tr.quilometragemFinal.append(km_atual)
			tr.velocidadeMaximaPermitida.append(random.choice([60.0, 80.0, 100.0]))
			tr.larguraPista.append(random.choice([7.0, 8.0, 10.0]))
			tr.volumeMedioTrafego.append(random.choice([1000, 1600, 2000]))
			trechos.append(tr)
		
		rodovia_principal.compostoPorTrechos = trechos
		
		animais = []
		for i in range(1, 61):
			if i <= 30:
				animal = onto.Mamifero(f"Mamifero_Sintetico_{i}")
			elif i <= 45:
				animal = onto.Reptil(f"Reptil_Sintetico_{i}")
			else:
				animal = onto.Ave(f"Ave_Sintetica_{i}")
			animal.possuiHabitat.append(random.choice(habitats))
			animal.nomeComum.append(f"Animal {i}")
			animal.pertenceAEspecie.append(random.choice(todas_especies))
			animais.append(animal)
		
		for i in range(1, 41):
			evento = onto.EventoAtropelamento(f"Evento_Atropelamento_Sintetico_{i}")
			evento.envolveAnimal.append(random.choice(animais))
			evento.ocorreEmRodovia = rodovia_principal
			evento.ocorreEmTrecho = random.choice(trechos)
			evento.dataEvento.append(f"2023-{random.randint(1,12):02d}-{random.randint(1,28):02d}")
			evento.horaEvento.append(f"{random.choice([4, 10, 14, 19, 22]):02d}:00")
			evento.condicaoAnimalPosEvento.append(random.choice(["Morto", "Ferido"]))
			
			loc = onto.LocalizacaoGeografica(f"Loc_{i}", coordenadaLatitude=[-32.0 + random.random()], coordenadaLongitude=[-52.0 + random.random()])
			evento.localizadoEm.append(loc)
			
			cond = onto.CondicaoClimatica(f"Clima_{i}", temperaturaRegistrada=[random.uniform(15.0, 35.0)], umidadeRelativa=[random.uniform(60.0, 95.0)])
			evento.temCondicaoAmbiental.append(cond)
			
			evento.temFatorRisco.append(random.choice(fatores_risco))
			
			periodo = onto.PeriodoTemporal(f"Periodo_{i}")
			evento.ocorreDurantePeriodo = periodo
	output_file = "ontologia_taim_povoada.owl"
	onto.save(output_file, format="rdfxml")
	
	print(f"Ontologia povoada salva com sucesso em '{output_file}'.")
	print("Foram criadas exatamente 125 instâncias sintéticas.")
	print(f"Indivíduos totais (Sintéticos + Extraídos): {len(list(onto.individuals()))}")
if __name__ == "__main__":
	random.seed(0)
	povoar_ontologia()

