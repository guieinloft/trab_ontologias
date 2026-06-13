import sys
from dataclasses import dataclass

PREFIXOS = """
PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:   <http://www.w3.org/2002/07/owl#>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
PREFIX taim:  <http://www.semanticweb.org/ontologias/banhado-do-taim/atropelamento-fauna.owl#>
""".strip()

@dataclass
class ConsultaSPARQL:
	codigo: str
	categoria: str
	titulo: str
	descricao: str
	resultado_esperado: str
	sparql: str

CONSULTAS: list[ConsultaSPARQL] = []

CONSULTAS.append(ConsultaSPARQL(
	codigo="Q01",
	categoria="A - Simples",
	titulo="Listar todos os animais registrados na ontologia",
	descricao=(
		"Recupera todos os indivíduos classificados como Animal (incluindo "
		"subclasses Mamifero, Reptil, Ave e Anfibio), retornando o identificador "
		"do indivíduo, seu nome comum e a classe taxonômica a que pertence."
	),
	resultado_esperado=(
		"Tabela com colunas: ?animal (IRI), ?nome (string), ?classe (IRI da subclasse). "
		"Uma linha por animal registrado."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?animal ?nome ?classe
WHERE {{
	?animal rdf:type ?classe .
	?classe rdfs:subClassOf* taim:Animal .
	?animal taim:nomeComum ?nome .
	FILTER (?classe != owl:NamedIndividual)
}}
ORDER BY ?classe ?nome
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q02",
	categoria="A - Simples",
	titulo="Listar todas as espécies com seu status de conservação",
	descricao=(
		"Recupera todas as instâncias da classe EspecieAnimal, retornando "
		"o nome científico (binômio latino), o nome comum vernacular e a "
		"categoria de ameaça segundo a IUCN/ICMBio."
	),
	resultado_esperado=(
		"Tabela com colunas: ?especie (IRI), ?nomeCientifico (string), "
		"?nomeComum (string), ?status (string). Uma linha por espécie."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?especie ?nomeCientifico ?nomeComum ?status
WHERE {{
	?especie rdf:type taim:EspecieAnimal .
	?especie taim:nomeCientifico ?nomeCientifico .
	?especie taim:nomeComum ?nomeComum .
	?especie taim:statusConservacao ?status .
}}
ORDER BY ?nomeCientifico
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q03",
	categoria="A - Simples",
	titulo="Listar todos os trechos rodoviários com suas características",
	descricao=(
		"Recupera todos os indivíduos da classe TrechoRodoviario com seus "
		"atributos operacionais: quilometragem inicial e final, velocidade "
		"máxima permitida, largura da pista e volume médio de tráfego."
	),
	resultado_esperado=(
		"Tabela com colunas: ?trecho, ?kmInicio, ?kmFim, ?velMax, "
		"?largura, ?volume. Uma linha por trecho."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?trecho ?kmInicio ?kmFim ?velMax ?largura ?volume
WHERE {{
	?trecho rdf:type taim:TrechoRodoviario .
	?trecho taim:quilometragemInicial ?kmInicio .
	?trecho taim:quilometragemFinal ?kmFim .
	?trecho taim:velocidadeMaximaPermitida ?velMax .
	?trecho taim:larguraPista ?largura .
	?trecho taim:volumeMedioTrafego ?volume .
}}
ORDER BY ?kmInicio
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q04",
	categoria="A - Simples",
	titulo="Listar todos os eventos de atropelamento com data e desfecho",
	descricao=(
		"Recupera todos os indivíduos da classe EventoAtropelamento, "
		"retornando a data do evento (ISO 8601), a hora local e a "
		"condição do animal após o evento (morto, ferido ou fuga)."
	),
	resultado_esperado=(
		"Tabela com colunas: ?evento, ?data, ?hora, ?condicao. "
		"Uma linha por evento registrado."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?evento ?data ?hora ?condicao
WHERE {{
	?evento rdf:type taim:EventoAtropelamento .
	?evento taim:dataEvento ?data .
	?evento taim:horaEvento ?hora .
	?evento taim:condicaoAnimalPosEvento ?condicao .
}}
ORDER BY ?data
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q05",
	categoria="A - Simples",
	titulo="Listar todas as medidas de mitigação cadastradas",
	descricao=(
		"Recupera todos os indivíduos da classe MedidaMitigacao, "
		"listando as intervenções disponíveis para redução do "
		"atropelamento de fauna na região do Taim."
	),
	resultado_esperado=(
		"Tabela com coluna: ?medida (IRI/nome local). "
		"Uma linha por medida de mitigação."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?medida
WHERE {{
	?medida rdf:type taim:MedidaMitigacao .
}}
ORDER BY ?medida
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q06",
	categoria="A - Simples",
	titulo="Listar todos os tipos de habitat (vegetação e corpos hídricos)",
	descricao=(
		"Recupera todos os indivíduos das subclasses de CaracteristicaHabitat "
		"(TipoVegetacao e CorpoHidrico), identificando a categoria de cada um."
	),
	resultado_esperado=(
		"Tabela com colunas: ?habitat (IRI), ?tipo (IRI da subclasse). "
		"Uma linha por habitat."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?habitat ?tipo
WHERE {{
	?habitat rdf:type ?tipo .
	?tipo rdfs:subClassOf taim:CaracteristicaHabitat .
	FILTER (?tipo != owl:NamedIndividual)
}}
ORDER BY ?tipo ?habitat
"""
))

CONSULTAS.append(ConsultaSPARQL(
	codigo="Q07",
	categoria="B - Complexa",
	titulo="Eventos de atropelamento com espécie, rodovia e trecho",
	descricao=(
		"Cruza as relações envolveAnimal, pertenceAEspecie, ocorreEmRodovia "
		"e ocorreEmTrecho para obter uma visão completa de cada evento: "
		"qual espécie foi atropelada, em qual rodovia e em qual trecho "
		"quilométrico, incluindo o nome científico."
	),
	resultado_esperado=(
		"Tabela com colunas: ?evento, ?nomeAnimal, ?nomeCientifico, "
		"?rodovia, ?trecho. Junção completa evento->animal->espécie + "
		"evento->rodovia + evento->trecho."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?evento ?nomeAnimal ?nomeCientifico ?rodovia ?trecho
WHERE {{
	?evento rdf:type taim:EventoAtropelamento .
	?evento taim:envolveAnimal ?animal .
	?animal taim:nomeComum ?nomeAnimal .
	?animal taim:pertenceAEspecie ?especie .
	?especie taim:nomeCientifico ?nomeCientifico .
	?evento taim:ocorreEmRodovia ?rodovia .
	?evento taim:ocorreEmTrecho ?trecho .
}}
ORDER BY ?evento
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q08",
	categoria="B - Complexa",
	titulo="Atropelamentos associados a habitats específicos via trecho",
	descricao=(
		"Cruza evento->trecho e trecho->habitat (atravessaHabitat) para "
		"identificar em quais tipos de habitat (vegetação ou corpo hídrico) "
		"os atropelamentos estão concentrados. Permite correlacionar a "
		"ocorrência de atropelamentos com a paisagem lindeira."
	),
	resultado_esperado=(
		"Tabela com colunas: ?evento, ?trecho, ?habitat, ?tipoHabitat. "
		"Múltiplas linhas por evento quando o trecho atravessa mais de um habitat."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?evento ?trecho ?habitat ?tipoHabitat
WHERE {{
	?evento rdf:type taim:EventoAtropelamento .
	?evento taim:ocorreEmTrecho ?trecho .
	?trecho taim:atravessaHabitat ?habitat .
	?habitat rdf:type ?tipoHabitat .
	FILTER (?tipoHabitat IN (taim:TipoVegetacao, taim:CorpoHidrico))
}}
ORDER BY ?evento ?tipoHabitat
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q09",
	categoria="B - Complexa",
	titulo="Animais atropelados cujo habitat é interceptado pelo trecho do evento",
	descricao=(
		"Consulta de tripla junção que identifica casos em que o animal "
		"atropelado possui um habitat (possuiHabitat) que é simultaneamente "
		"atravessado (atravessaHabitat) pelo trecho rodoviário onde o evento "
		"ocorreu. Evidencia a sobreposição espacial animal-rodovia-habitat."
	),
	resultado_esperado=(
		"Tabela com colunas: ?evento, ?animal, ?trecho, ?habitatCompartilhado. "
		"Somente eventos onde há interseção habitat-do-animal ∩ habitat-do-trecho."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?evento ?animal ?trecho ?habitatCompartilhado
WHERE {{
	?evento rdf:type taim:EventoAtropelamento .
	?evento taim:envolveAnimal ?animal .
	?evento taim:ocorreEmTrecho ?trecho .
	?animal taim:possuiHabitat ?habitatCompartilhado .
	?trecho taim:atravessaHabitat ?habitatCompartilhado .
}}
ORDER BY ?evento
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q10",
	categoria="B - Complexa",
	titulo="Fatores de risco dos eventos e medidas de mitigação disponíveis",
	descricao=(
		"Cruza evento->fatorRisco e fatorRisco->mitigação para construir "
		"a cadeia completa: qual evento sofreu qual fator de risco e quais "
		"medidas de mitigação poderiam atenuá-lo. Inclui o tipo do fator "
		"(antrópico ou ecológico)."
	),
	resultado_esperado=(
		"Tabela com colunas: ?evento, ?fator, ?tipoFator, ?medida. "
		"Múltiplas linhas por evento quando há múltiplos fatores/medidas."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?evento ?fator ?tipoFator ?medida
WHERE {{
	?evento rdf:type taim:EventoAtropelamento .
	?evento taim:temFatorRisco ?fator .
	?fator rdf:type ?tipoFator .
	?fator taim:mitigadoPor ?medida .
	FILTER (?tipoFator IN (taim:FatorAntropico, taim:FatorEcologico))
}}
ORDER BY ?evento ?tipoFator
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q11",
	categoria="B - Complexa",
	titulo="Cadeia completa: evento -> animal -> espécie -> habitat -> trecho -> localização",
	descricao=(
		"Consulta de junção de 6 vias que reconstrói a cadeia semântica "
		"completa do evento até a localização geográfica, cruzando todas "
		"as relações centrais da ontologia. Permite rastrear a proveniência "
		"ecológica e espacial completa de cada atropelamento."
	),
	resultado_esperado=(
		"Tabela com colunas: ?evento, ?nomeAnimal, ?nomeCientifico, "
		"?habitat, ?trecho, ?lat, ?lon. Visão integrada multidimensional."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?evento ?nomeAnimal ?nomeCientifico ?habitat ?trecho ?lat ?lon
WHERE {{
	?evento rdf:type taim:EventoAtropelamento .
	?evento taim:envolveAnimal ?animal .
	?animal taim:nomeComum ?nomeAnimal .
	?animal taim:pertenceAEspecie ?especie .
	?especie taim:nomeCientifico ?nomeCientifico .
	?animal taim:possuiHabitat ?habitat .
	?evento taim:ocorreEmTrecho ?trecho .
	?evento taim:localizadoEm ?loc .
	?loc taim:coordenadaLatitude ?lat .
	?loc taim:coordenadaLongitude ?lon .
}}
ORDER BY ?evento
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q12",
	categoria="B - Complexa",
	titulo="Espécies ameaçadas atropeladas em trechos com alto volume de tráfego",
	descricao=(
		"Cruza evento->animal->espécie (filtro: status ≠ 'LC') com "
		"evento->trecho (filtro: volumeMedioTrafego > 1500) para identificar "
		"casos críticos onde espécies não classificadas como 'Least Concern' "
		"são atropeladas em trechos de alto fluxo veicular."
	),
	resultado_esperado=(
		"Tabela com colunas: ?evento, ?nomeCientifico, ?status, "
		"?trecho, ?volume. Somente espécies com status diferente de 'LC' "
		"em trechos com volume > 1500 veíc/dia."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?evento ?nomeCientifico ?status ?trecho ?volume
WHERE {{
	?evento rdf:type taim:EventoAtropelamento .
	?evento taim:envolveAnimal ?animal .
	?animal taim:pertenceAEspecie ?especie .
	?especie taim:nomeCientifico ?nomeCientifico .
	?especie taim:statusConservacao ?status .
	?evento taim:ocorreEmTrecho ?trecho .
	?trecho taim:volumeMedioTrafego ?volume .
	FILTER (?status != "LC")
	FILTER (?volume > 1500)
}}
ORDER BY ?status DESC(?volume)
"""
))

CONSULTAS.append(ConsultaSPARQL(
	codigo="Q13",
	categoria="C - Filtros Operacionais",
	titulo="Atropelamentos ocorridos no período noturno (entre 18:00 e 06:00)",
	descricao=(
		"Filtra eventos cuja hora de registro (horaEvento) indica "
		"ocorrência noturna (≥ 18:00 ou < 06:00), correspondendo ao "
		"período de maior atividade de espécies crepusculares e noturnas."
	),
	resultado_esperado=(
		"Tabela com colunas: ?evento, ?hora, ?nomeAnimal, ?data. "
		"Somente eventos noturnos."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?evento ?hora ?nomeAnimal ?data
WHERE {{
	?evento rdf:type taim:EventoAtropelamento .
	?evento taim:horaEvento ?hora .
	?evento taim:dataEvento ?data .
	?evento taim:envolveAnimal ?animal .
	?animal taim:nomeComum ?nomeAnimal .
	FILTER (?hora >= "18:00" || ?hora < "06:00")
}}
ORDER BY ?hora
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q14",
	categoria="C - Filtros Operacionais",
	titulo="Atropelamentos sob temperatura elevada (> 25°C)",
	descricao=(
		"Filtra eventos associados a condições climáticas onde a temperatura "
		"registrada ultrapassa 25°C, cenário relevante para répteis que "
		"utilizam o asfalto para termorregulação."
	),
	resultado_esperado=(
		"Tabela com colunas: ?evento, ?nomeAnimal, ?temperatura, ?umidade. "
		"Somente eventos com temperatura > 25°C."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?evento ?nomeAnimal ?temperatura ?umidade
WHERE {{
	?evento rdf:type taim:EventoAtropelamento .
	?evento taim:envolveAnimal ?animal .
	?animal taim:nomeComum ?nomeAnimal .
	?evento taim:temCondicaoAmbiental ?cond .
	?cond rdf:type taim:CondicaoClimatica .
	?cond taim:temperaturaRegistrada ?temperatura .
	?cond taim:umidadeRelativa ?umidade .
	FILTER (?temperatura > 25.0)
}}
ORDER BY DESC(?temperatura)
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q15",
	categoria="C - Filtros Operacionais",
	titulo="Atropelamentos em trechos com velocidade máxima ≥ 80 km/h",
	descricao=(
		"Filtra eventos que ocorreram em trechos rodoviários onde a "
		"velocidade regulamentar é igual ou superior a 80 km/h, "
		"condição que reduz o tempo de reação do condutor e eleva "
		"a letalidade do atropelamento."
	),
	resultado_esperado=(
		"Tabela com colunas: ?evento, ?trecho, ?velMax, ?nomeAnimal. "
		"Somente trechos com velocidade ≥ 80."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?evento ?trecho ?velMax ?nomeAnimal
WHERE {{
	?evento rdf:type taim:EventoAtropelamento .
	?evento taim:ocorreEmTrecho ?trecho .
	?trecho taim:velocidadeMaximaPermitida ?velMax .
	?evento taim:envolveAnimal ?animal .
	?animal taim:nomeComum ?nomeAnimal .
	FILTER (?velMax >= 80)
}}
ORDER BY DESC(?velMax)
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q16",
	categoria="C - Filtros Operacionais",
	titulo="Atropelamentos com alta umidade relativa (> 80%) em período noturno",
	descricao=(
		"Filtro composto que identifica eventos ocorridos sob duas "
		"condições simultâneas: alta umidade relativa (> 80%) e período "
		"noturno. Cenário associado à movimentação de anfíbios durante "
		"noites úmidas."
	),
	resultado_esperado=(
		"Tabela com colunas: ?evento, ?hora, ?umidade, ?nomeAnimal. "
		"Somente eventos noturnos E com umidade > 80%."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?evento ?hora ?umidade ?nomeAnimal
WHERE {{
	?evento rdf:type taim:EventoAtropelamento .
	?evento taim:horaEvento ?hora .
	?evento taim:envolveAnimal ?animal .
	?animal taim:nomeComum ?nomeAnimal .
	?evento taim:temCondicaoAmbiental ?cond .
	?cond rdf:type taim:CondicaoClimatica .
	?cond taim:umidadeRelativa ?umidade .
	FILTER (?umidade > 80.0)
	FILTER (?hora >= "18:00" || ?hora < "06:00")
}}
ORDER BY DESC(?umidade)
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q17",
	categoria="C - Filtros Operacionais",
	titulo="Eventos em trechos estreitos (largura < 7.5m) com alto tráfego",
	descricao=(
		"Identifica atropelamentos em trechos que combinam pista estreita "
		"(< 7.5 metros) e volume de tráfego superior a 1500 veículos/dia, "
		"condições que limitam manobras evasivas."
	),
	resultado_esperado=(
		"Tabela com colunas: ?evento, ?trecho, ?largura, ?volume, ?nomeAnimal. "
		"Somente trechos com largura < 7.5m E volume > 1500."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?evento ?trecho ?largura ?volume ?nomeAnimal
WHERE {{
	?evento rdf:type taim:EventoAtropelamento .
	?evento taim:ocorreEmTrecho ?trecho .
	?trecho taim:larguraPista ?largura .
	?trecho taim:volumeMedioTrafego ?volume .
	?evento taim:envolveAnimal ?animal .
	?animal taim:nomeComum ?nomeAnimal .
	FILTER (?largura < 7.5)
	FILTER (?volume > 1500)
}}
ORDER BY ?largura DESC(?volume)
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q18",
	categoria="C - Filtros Operacionais",
	titulo="Atropelamentos de répteis em eventos com temperatura entre 20°C e 30°C",
	descricao=(
		"Filtra exclusivamente atropelamentos de répteis (classe Reptil) "
		"associados a condições climáticas com temperatura na faixa de "
		"20°C a 30°C, intervalo ótimo para termorregulação ectotérmica "
		"no asfalto."
	),
	resultado_esperado=(
		"Tabela com colunas: ?evento, ?nomeAnimal, ?nomeCientifico, "
		"?temperatura. Somente répteis dentro da faixa térmica."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?evento ?nomeAnimal ?nomeCientifico ?temperatura
WHERE {{
	?evento rdf:type taim:EventoAtropelamento .
	?evento taim:envolveAnimal ?animal .
	?animal rdf:type taim:Reptil .
	?animal taim:nomeComum ?nomeAnimal .
	?animal taim:pertenceAEspecie ?especie .
	?especie taim:nomeCientifico ?nomeCientifico .
	?evento taim:temCondicaoAmbiental ?cond .
	?cond rdf:type taim:CondicaoClimatica .
	?cond taim:temperaturaRegistrada ?temperatura .
	FILTER (?temperatura >= 20.0 && ?temperatura <= 30.0)
}}
ORDER BY ?temperatura
"""
))

CONSULTAS.append(ConsultaSPARQL(
	codigo="Q19",
	categoria="D - Agregação",
	titulo="Contagem total de atropelamentos por classe taxonômica",
	descricao=(
		"Agrega o número de eventos de atropelamento por classe taxonômica "
		"do animal envolvido (Mamifero, Reptil, Ave, Anfibio), permitindo "
		"identificar qual grupo faunístico é mais impactado."
	),
	resultado_esperado=(
		"Tabela com colunas: ?classeTaxonomica (IRI), ?totalAtropelamentos "
		"(inteiro). Uma linha por classe, ordenada de forma decrescente."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?classeTaxonomica (COUNT(?evento) AS ?totalAtropelamentos)
WHERE {{
	?evento rdf:type taim:EventoAtropelamento .
	?evento taim:envolveAnimal ?animal .
	?animal rdf:type ?classeTaxonomica .
	FILTER (?classeTaxonomica IN (
		taim:Mamifero, taim:Reptil, taim:Ave, taim:Anfibio
	))
}}
GROUP BY ?classeTaxonomica
ORDER BY DESC(?totalAtropelamentos)
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q20",
	categoria="D - Agregação",
	titulo="Contagem de atropelamentos por trecho rodoviário (hotspots)",
	descricao=(
		"Agrega o número de eventos por trecho rodoviário para identificar "
		"os segmentos de rodovia com maior concentração de atropelamentos "
		"(hotspots), informação essencial para priorização de intervenções."
	),
	resultado_esperado=(
		"Tabela com colunas: ?trecho (IRI), ?kmInicio, ?kmFim, "
		"?totalEventos (inteiro). Ordenada por frequência decrescente."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?trecho ?kmInicio ?kmFim (COUNT(?evento) AS ?totalEventos)
WHERE {{
	?evento rdf:type taim:EventoAtropelamento .
	?evento taim:ocorreEmTrecho ?trecho .
	?trecho taim:quilometragemInicial ?kmInicio .
	?trecho taim:quilometragemFinal ?kmFim .
}}
GROUP BY ?trecho ?kmInicio ?kmFim
ORDER BY DESC(?totalEventos)
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q21",
	categoria="D - Agregação",
	titulo="Temperatura média e máxima nos eventos de atropelamento",
	descricao=(
		"Calcula a temperatura média e a temperatura máxima registradas "
		"nos eventos de atropelamento que possuem condição climática "
		"associada, fornecendo uma visão estatística do perfil térmico "
		"dos atropelamentos."
	),
	resultado_esperado=(
		"Tabela com colunas: ?tempMedia (float), ?tempMaxima (float), "
		"?totalComDados (inteiro). Uma única linha de resultado."
	),
	sparql=f"""
{PREFIXOS}
SELECT (AVG(?temp) AS ?tempMedia) (MAX(?temp) AS ?tempMaxima)
	   (COUNT(?evento) AS ?totalComDados)
WHERE {{
	?evento rdf:type taim:EventoAtropelamento .
	?evento taim:temCondicaoAmbiental ?cond .
	?cond rdf:type taim:CondicaoClimatica .
	?cond taim:temperaturaRegistrada ?temp .
}}
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q22",
	categoria="D - Agregação",
	titulo="Contagem de atropelamentos por período temporal",
	descricao=(
		"Agrega o número de eventos por PeriodoTemporal (estação do ano, "
		"turno do dia), revelando a distribuição temporal dos atropelamentos "
		"e potenciais padrões sazonais ou circadianos."
	),
	resultado_esperado=(
		"Tabela com colunas: ?periodo (IRI), ?totalEventos (inteiro). "
		"Uma linha por período temporal."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?periodo (COUNT(?evento) AS ?totalEventos)
WHERE {{
	?evento rdf:type taim:EventoAtropelamento .
	?evento taim:ocorreDurantePeriodo ?periodo .
}}
GROUP BY ?periodo
ORDER BY DESC(?totalEventos)
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q23",
	categoria="D - Agregação",
	titulo="Contagem de fatores de risco por tipo (antrópico vs. ecológico)",
	descricao=(
		"Agrega a frequência com que cada tipo de fator de risco "
		"(FatorAntropico ou FatorEcologico) é associado a eventos, "
		"quantificando a contribuição relativa de causas humanas "
		"versus ecológicas."
	),
	resultado_esperado=(
		"Tabela com colunas: ?tipoFator (IRI), ?totalOcorrencias (inteiro). "
		"Duas linhas: uma para antrópico, uma para ecológico."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?tipoFator (COUNT(?evento) AS ?totalOcorrencias)
WHERE {{
	?evento rdf:type taim:EventoAtropelamento .
	?evento taim:temFatorRisco ?fator .
	?fator rdf:type ?tipoFator .
	FILTER (?tipoFator IN (taim:FatorAntropico, taim:FatorEcologico))
}}
GROUP BY ?tipoFator
ORDER BY DESC(?totalOcorrencias)
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q24",
	categoria="D - Agregação",
	titulo="Número de habitats distintos por animal e contagem de espécies por habitat",
	descricao=(
		"Duas subconsultas: (a) conta quantos habitats distintos cada "
		"animal utiliza; (b) conta quantos animais distintos estão "
		"associados a cada habitat. Permite identificar espécies "
		"generalistas vs. especialistas e habitats mais biodiversos."
	),
	resultado_esperado=(
		"Tabela com colunas: ?animal, ?nomeAnimal, ?qtdHabitats (inteiro). "
		"Uma linha por animal, ordenada pela diversidade de habitats."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?animal ?nomeAnimal (COUNT(DISTINCT ?habitat) AS ?qtdHabitats)
WHERE {{
	?animal rdf:type/rdfs:subClassOf* taim:Animal .
	?animal taim:nomeComum ?nomeAnimal .
	?animal taim:possuiHabitat ?habitat .
}}
GROUP BY ?animal ?nomeAnimal
ORDER BY DESC(?qtdHabitats)
"""
))

CONSULTAS.append(ConsultaSPARQL(
	codigo="Q25",
	categoria="E - Cenário Operacional",
	titulo="Identificação de hotspots: trechos com atropelamento E sobreposição de habitat",
	descricao=(
		"Cenário: equipe de fiscalização da ESEC Taim precisa identificar "
		"trechos rodoviários onde (a) já ocorreram atropelamentos e (b) o "
		"habitat do animal atropelado é interceptado pela rodovia. Esses "
		"trechos são candidatos prioritários para instalação de passagens "
		"de fauna."
	),
	resultado_esperado=(
		"Tabela com colunas: ?trecho, ?kmInicio, ?kmFim, ?nomeAnimal, "
		"?habitatComum, ?velMax. Trechos priorizáveis para mitigação."
	),
	sparql=f"""
{PREFIXOS}
SELECT DISTINCT ?trecho ?kmInicio ?kmFim ?nomeAnimal ?habitatComum ?velMax
WHERE {{
	?evento rdf:type taim:EventoAtropelamento .
	?evento taim:envolveAnimal ?animal .
	?animal taim:nomeComum ?nomeAnimal .
	?animal taim:possuiHabitat ?habitatComum .
	?evento taim:ocorreEmTrecho ?trecho .
	?trecho taim:atravessaHabitat ?habitatComum .
	?trecho taim:quilometragemInicial ?kmInicio .
	?trecho taim:quilometragemFinal ?kmFim .
	?trecho taim:velocidadeMaximaPermitida ?velMax .
}}
ORDER BY ?kmInicio
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q26",
	categoria="E - Cenário Operacional",
	titulo="Planejamento de redutores de velocidade: trechos onde fator antrópico é mitigável",
	descricao=(
		"Cenário: o DNIT solicita recomendações para instalação de "
		"redutores de velocidade. A consulta identifica trechos onde "
		"atropelamentos tiveram fator de risco antrópico (ex: velocidade "
		"excessiva) que pode ser mitigado por redutor de velocidade, "
		"cruzando evento->fator->medida com evento->trecho."
	),
	resultado_esperado=(
		"Tabela com colunas: ?trecho, ?kmInicio, ?kmFim, ?fator, ?medida, "
		"?velMax. Trechos elegíveis para intervenção de engenharia."
	),
	sparql=f"""
{PREFIXOS}
SELECT DISTINCT ?trecho ?kmInicio ?kmFim ?fator ?medida ?velMax
WHERE {{
	?evento rdf:type taim:EventoAtropelamento .
	?evento taim:ocorreEmTrecho ?trecho .
	?trecho taim:quilometragemInicial ?kmInicio .
	?trecho taim:quilometragemFinal ?kmFim .
	?trecho taim:velocidadeMaximaPermitida ?velMax .
	?evento taim:temFatorRisco ?fator .
	?fator rdf:type taim:FatorAntropico .
	?fator taim:mitigadoPor ?medida .
}}
ORDER BY DESC(?velMax)
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q27",
	categoria="E - Cenário Operacional",
	titulo="Alerta migratório: espécies com fator ecológico de migração sazonal",
	descricao=(
		"Cenário: durante o planejamento de campanhas de monitoramento, "
		"a equipe precisa saber quais espécies estão associadas a eventos "
		"cujo fator de risco é a migração sazonal, para intensificar a "
		"vigilância nos períodos migratórios. Cruza evento->animal->espécie "
		"com evento->fator(migração)->período."
	),
	resultado_esperado=(
		"Tabela com colunas: ?especie, ?nomeCientifico, ?nomeComum, "
		"?periodo, ?trecho. Espécies com risco migratório e os trechos/períodos afetados."
	),
	sparql=f"""
{PREFIXOS}
SELECT DISTINCT ?nomeCientifico ?nomeComum ?periodo ?trecho
WHERE {{
	?evento rdf:type taim:EventoAtropelamento .
	?evento taim:envolveAnimal ?animal .
	?animal taim:pertenceAEspecie ?especie .
	?especie taim:nomeCientifico ?nomeCientifico .
	?especie taim:nomeComum ?nomeComum .
	?evento taim:temFatorRisco ?fator .
	?fator rdf:type taim:FatorEcologico .
	?evento taim:ocorreDurantePeriodo ?periodo .
	?evento taim:ocorreEmTrecho ?trecho .
}}
ORDER BY ?nomeCientifico
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q28",
	categoria="E - Cenário Operacional",
	titulo="Mapeamento georreferenciado: coordenadas de todos os eventos com classe taxonômica",
	descricao=(
		"Cenário: para integração com SIG (Sistema de Informação "
		"Geográfica), extraem-se as coordenadas WGS 84 de cada evento "
		"junto com a classe taxonômica do animal, gerando dados prontos "
		"para sobreposição em camadas cartográficas."
	),
	resultado_esperado=(
		"Tabela com colunas: ?evento, ?lat, ?lon, ?classeTaxonomica, "
		"?nomeAnimal, ?data. Dados georreferenciados para GIS."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?evento ?lat ?lon ?classeTaxonomica ?nomeAnimal ?data
WHERE {{
	?evento rdf:type taim:EventoAtropelamento .
	?evento taim:localizadoEm ?loc .
	?loc taim:coordenadaLatitude ?lat .
	?loc taim:coordenadaLongitude ?lon .
	?evento taim:envolveAnimal ?animal .
	?animal rdf:type ?classeTaxonomica .
	?animal taim:nomeComum ?nomeAnimal .
	?evento taim:dataEvento ?data .
	FILTER (?classeTaxonomica IN (
		taim:Mamifero, taim:Reptil, taim:Ave, taim:Anfibio
	))
}}
ORDER BY ?data
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q29",
	categoria="E - Cenário Operacional",
	titulo="Avaliação de eficácia: fatores de risco sem medida de mitigação associada",
	descricao=(
		"Cenário: auditoria de gestão da ESEC Taim busca identificar "
		"fatores de risco presentes nos eventos que não possuem nenhuma "
		"medida de mitigação cadastrada na ontologia. Esses fatores "
		"representam lacunas de gestão onde intervenções são necessárias."
	),
	resultado_esperado=(
		"Tabela com colunas: ?fator (IRI), ?tipoFator (IRI). "
		"Somente fatores de risco sem medida mitigadora associada."
	),
	sparql=f"""
{PREFIXOS}
SELECT DISTINCT ?fator ?tipoFator
WHERE {{
	?evento rdf:type taim:EventoAtropelamento .
	?evento taim:temFatorRisco ?fator .
	?fator rdf:type ?tipoFator .
	FILTER (?tipoFator IN (taim:FatorAntropico, taim:FatorEcologico))
	FILTER NOT EXISTS {{
		?fator taim:mitigadoPor ?medida .
	}}
}}
ORDER BY ?tipoFator ?fator
"""
))
CONSULTAS.append(ConsultaSPARQL(
	codigo="Q30",
	categoria="E - Cenário Operacional",
	titulo="Relatório integrado de risco: índice composto por trecho",
	descricao=(
		"Cenário: relatório gerencial que atribui a cada trecho rodoviário "
		"um perfil de risco agregado, combinando: número de eventos, número "
		"de fatores de risco distintos, número de habitats interceptados "
		"e a velocidade máxima permitida. Informação crítica para "
		"priorização orçamentária de intervenções."
	),
	resultado_esperado=(
		"Tabela com colunas: ?trecho, ?kmInicio, ?kmFim, ?velMax, "
		"?qtdEventos, ?qtdFatores, ?qtdHabitats. Uma linha por trecho, "
		"ordenada por quantidade de eventos decrescente."
	),
	sparql=f"""
{PREFIXOS}
SELECT ?trecho ?kmInicio ?kmFim ?velMax
	   (COUNT(DISTINCT ?evento) AS ?qtdEventos)
	   (COUNT(DISTINCT ?fator) AS ?qtdFatores)
	   (COUNT(DISTINCT ?habitat) AS ?qtdHabitats)
WHERE {{
	?trecho rdf:type taim:TrechoRodoviario .
	?trecho taim:quilometragemInicial ?kmInicio .
	?trecho taim:quilometragemFinal ?kmFim .
	?trecho taim:velocidadeMaximaPermitida ?velMax .
	OPTIONAL {{
		?evento taim:ocorreEmTrecho ?trecho .
		OPTIONAL {{ ?evento taim:temFatorRisco ?fator . }}
	}}
	OPTIONAL {{
		?trecho taim:atravessaHabitat ?habitat .
	}}
}}
GROUP BY ?trecho ?kmInicio ?kmFim ?velMax
ORDER BY DESC(?qtdEventos) DESC(?velMax)
"""
))

SEPARADOR = "-" * 78
def imprimir_consultas() -> None:
	categoria_atual = ""
	print("\n=== CONSULTAS SPARQL - ONTOLOGIA DO BANHADO DO TAIM ===")
	for i, q in enumerate(CONSULTAS, 1):

		if q.categoria != categoria_atual:
			categoria_atual = q.categoria
			print(f"\n### CATEGORIA: {categoria_atual.upper()} ###")

		print(f"\n[{q.codigo}] {q.titulo}")
		print(f"\n  DESCRIÇÃO:")

		palavras = q.descricao.split()
		linha = "	"
		for p in palavras:
			if len(linha) + len(p) + 1 > 74:
				print(linha)
				linha = "	" + p
			else:
				linha += " " + p if linha.strip() else "	" + p
		if linha.strip():
			print(linha)
		print(f"\n  RESULTADO ESPERADO:")
		palavras = q.resultado_esperado.split()
		linha = "	"
		for p in palavras:
			if len(linha) + len(p) + 1 > 74:
				print(linha)
				linha = "	" + p
			else:
				linha += " " + p if linha.strip() else "	" + p
		if linha.strip():
			print(linha)
		print(f"\n  CÓDIGO SPARQL:")
		for ln in q.sparql.strip().split("\n"):
			print(f"	{ln}")
		print()
def executar_com_rdflib(owl_path: str = "ontologia_taim.owl") -> None:
	try:
		from rdflib import Graph
	except ImportError:
		print("\n  [!] rdflib não instalado. Instale com: pip install rdflib")
		print("	  As consultas foram impressas acima para execução manual.\n")
		return
	print("\n=== EXECUCAO DAS CONSULTAS VIA RDFLIB ===")
	g = Graph()
	try:
		g.parse(owl_path, format="xml")
		print(f"  OK Ontologia carregada: {owl_path}")
		print(f"	Triplas no grafo: {len(g)}\n")
	except Exception as e:
		print(f"  ERRO Erro ao carregar {owl_path}: {e}")
		return
	for q in CONSULTAS:
		print(f"\n{'-' * 78}")
		print(f"  [{q.codigo}] {q.titulo}")
		print(f"{'-' * 78}")
		try:
			results = g.query(q.sparql)
			if results:
				linhas = list(results)
				print(f"  -> {len(linhas)} resultado(s):\n")
				for row in linhas:
					valores = []
					for v in row:
						if v is None:
							valores.append("NULL")
						else:
							s = str(v)

							if "#" in s:
								s = s.split("#")[-1]
							valores.append(s)
					print(f"	{' | '.join(valores)}")
			else:
				print("  -> 0 resultados (conjunto vazio)")
		except Exception as e:
			print(f"  ERRO Erro na execução: {e}")
	print(f"\n  Execução concluída. {len(CONSULTAS)} consultas processadas.\n")
if __name__ == "__main__":
	imprimir_consultas()

	import os
	if os.path.exists("ontologia_taim_povoada.owl"):
		executar_com_rdflib("ontologia_taim_povoada.owl")
	else:
		print("\n  [i] Arquivo ontologia_taim_povoada.owl não encontrado.")
		print("	  Execute ontologia_taim.py primeiro para gerá-lo.\n")


