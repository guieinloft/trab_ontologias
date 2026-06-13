import os
from owlready2 import *
def gerar_ontologia():
	onto = get_ontology("http://www.semanticweb.org/ontologias/banhado-do-taim/atropelamento-fauna.owl")
	
	with onto:
		class Animal(Thing): pass
		class Mamifero(Animal): pass
		class Reptil(Animal): pass
		class Ave(Animal): pass
		class Anfibio(Animal): pass
		
		class EspecieAnimal(Thing): pass
		
		class Rodovia(Thing): pass
		class TrechoRodoviario(Thing): pass
		
		class EventoAtropelamento(Thing): pass
		
		class CondicaoAmbiental(Thing): pass
		class CondicaoClimatica(CondicaoAmbiental): pass
		class CondicaoLuminosidade(CondicaoAmbiental): pass
		
		class CaracteristicaHabitat(Thing): pass
		class TipoVegetacao(CaracteristicaHabitat): pass
		class CorpoHidrico(CaracteristicaHabitat): pass
		
		class FatorRisco(Thing): pass
		class FatorAntropico(FatorRisco): pass
		class FatorEcologico(FatorRisco): pass
		
		class LocalizacaoGeografica(Thing): pass
		class PeriodoTemporal(Thing): pass
		class MedidaMitigacao(Thing): pass
		class possuiHabitat(ObjectProperty):
			domain = [Animal, EspecieAnimal]
			range = [CaracteristicaHabitat]
		class localizadoEm(ObjectProperty):
			domain = [Thing]
			range = [LocalizacaoGeografica]
		class atravessaHabitat(ObjectProperty):
			domain = [Rodovia, TrechoRodoviario]
			range = [CaracteristicaHabitat]
		class envolveAnimal(ObjectProperty):
			domain = [EventoAtropelamento]
			range = [Animal]
		class pertenceAEspecie(ObjectProperty):
			domain = [Animal]
			range = [EspecieAnimal]
		class temFatorRisco(ObjectProperty):
			domain = [EventoAtropelamento, Animal]
			range = [FatorRisco]
		class mitigadoPor(ObjectProperty):
			domain = [FatorRisco, TrechoRodoviario, EventoAtropelamento]
			range = [MedidaMitigacao]
		class compostoPorTrechos(ObjectProperty):
			domain = [Rodovia]
			range = [TrechoRodoviario]
		class adjacenteA(ObjectProperty):
			domain = [CaracteristicaHabitat]
			range = [CaracteristicaHabitat]
		class ocorreEmRodovia(ObjectProperty, FunctionalProperty):
			domain = [EventoAtropelamento]
			range = [Rodovia]
		class ocorreEmTrecho(ObjectProperty, FunctionalProperty):
			domain = [EventoAtropelamento]
			range = [TrechoRodoviario]
		class ocorreDurantePeriodo(ObjectProperty, FunctionalProperty):
			domain = [EventoAtropelamento]
			range = [PeriodoTemporal]
		class temCondicaoAmbiental(ObjectProperty):
			domain = [EventoAtropelamento]
			range = [CondicaoAmbiental]
		class nomeComum(DataProperty): domain = [Animal, EspecieAnimal]; range = [str]
		class nomeCientifico(DataProperty): domain = [EspecieAnimal]; range = [str]
		class statusConservacao(DataProperty): domain = [EspecieAnimal]; range = [str]
		class quilometragemInicial(DataProperty): domain = [TrechoRodoviario]; range = [float]
		class quilometragemFinal(DataProperty): domain = [TrechoRodoviario]; range = [float]
		class velocidadeMaximaPermitida(DataProperty): domain = [Rodovia, TrechoRodoviario]; range = [float]
		class larguraPista(DataProperty): domain = [Rodovia, TrechoRodoviario]; range = [float]
		class volumeMedioTrafego(DataProperty): domain = [TrechoRodoviario]; range = [int]
		class temperaturaRegistrada(DataProperty): domain = [CondicaoClimatica]; range = [float]
		class umidadeRelativa(DataProperty): domain = [CondicaoClimatica]; range = [float]
		class precipitacaoTotal(DataProperty): domain = [CondicaoClimatica]; range = [float]
		class dataEvento(DataProperty): domain = [EventoAtropelamento]; range = [str]
		class horaEvento(DataProperty): domain = [EventoAtropelamento]; range = [str]
		class condicaoAnimalPosEvento(DataProperty): domain = [EventoAtropelamento]; range = [str]
		class coordenadaLatitude(DataProperty): domain = [LocalizacaoGeografica]; range = [float]
		class coordenadaLongitude(DataProperty): domain = [LocalizacaoGeografica]; range = [float]
		class numIndividuos(DataProperty): domain = [EventoAtropelamento]; range = [int]
	output_file = "ontologia_taim.owl"
	onto.save(output_file, format="rdfxml")
	
	print(f"Esquema da ontologia (TBox) salvo com sucesso em '{output_file}'.")
	print(f"Classes cadastradas: {len(list(onto.classes()))}")
	print(f"Propriedades cadastradas: {len(list(onto.properties()))}")
if __name__ == "__main__":
	gerar_ontologia()

