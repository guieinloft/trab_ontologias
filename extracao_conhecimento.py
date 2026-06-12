					  
					   
import csv
import json
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup, Tag
import spacy
from spacy.tokens import Doc, Span
																			  
						 
																			  
																			  
					   
																			  
						 
URLS_WIKIPEDIA = [
	"https://pt.wikipedia.org/wiki/Esta%C3%A7%C3%A3o_Ecol%C3%B3gica_do_Taim",
	"https://pt.wikipedia.org/wiki/Lagoa_Mirim",
	"https://pt.wikipedia.org/wiki/BR-471",
	"https://pt.wikipedia.org/wiki/Banhado",
	"https://pt.wikipedia.org/wiki/Cerdocyon_thous",
	"https://pt.wikipedia.org/wiki/Caiman_latirostris",
	"https://pt.wikipedia.org/wiki/Hydrochoerus_hydrochaeris",
]
URLS_ARTIGOS = [
	"https://periodicos.ufpel.edu.br/index.php/revbio/article/view/25384",
]
URLS_NOTICIAS = [
	"http://g1.globo.com/rs/rio-grande-do-sul/campo-e-lavoura/noticia/2013/10/estacao-do-taim-deve-ser-ampliada-ate-o-final-de-2014-no-rs-diz-icmbio.html",
	"http://www.oeco.org.br/reportagens/henrique-horn-ampliacao-da-esec-de-taim-e-consenso/",
]
																
														   
WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
WIKIDATA_QUERIES = [
	{
		"name": "Caiman latirostris",
		"query": """SELECT ?item ?itemLabel ?statusLabel ?habitatLabel WHERE {
  ?item wdt:P225 "Caiman latirostris" .
  OPTIONAL { ?item wdt:P141 ?status . }
  OPTIONAL { ?item wdt:P2974 ?habitat . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "pt,en". }
}"""
	},
	{
		"name": "Hydrochoerus hydrochaeris",
		"query": """SELECT ?item ?itemLabel ?statusLabel ?habitatLabel WHERE {
  ?item wdt:P225 "Hydrochoerus hydrochaeris" .
  OPTIONAL { ?item wdt:P141 ?status . }
  OPTIONAL { ?item wdt:P2974 ?habitat . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "pt,en". }
}"""
	},
	{
		"name": "Cerdocyon thous",
		"query": """SELECT ?item ?itemLabel ?statusLabel ?habitatLabel WHERE {
  ?item wdt:P225 "Cerdocyon thous" .
  OPTIONAL { ?item wdt:P141 ?status . }
  OPTIONAL { ?item wdt:P2974 ?habitat . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "pt,en". }
}"""
	},
	{
		"name": "Athene cunicularia",
		"query": """SELECT ?item ?itemLabel ?statusLabel ?habitatLabel WHERE {
  ?item wdt:P225 "Athene cunicularia" .
  OPTIONAL { ?item wdt:P141 ?status . }
  OPTIONAL { ?item wdt:P2974 ?habitat . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "pt,en". }
}"""
	},
	{
		"name": "Myocastor coypus",
		"query": """SELECT ?item ?itemLabel ?statusLabel ?habitatLabel WHERE {
  ?item wdt:P225 "Myocastor coypus" .
  OPTIONAL { ?item wdt:P141 ?status . }
  OPTIONAL { ?item wdt:P2974 ?habitat . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "pt,en". }
}"""
	},
	{
		"name": "Cygnus melancoryphus",
		"query": """SELECT ?item ?itemLabel ?statusLabel ?habitatLabel WHERE {
  ?item wdt:P225 "Cygnus melancoryphus" .
  OPTIONAL { ?item wdt:P141 ?status . }
  OPTIONAL { ?item wdt:P2974 ?habitat . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "pt,en". }
}"""
	},
]
																	
IBGE_API_URLS = [
	{
		"name": "Rio Grande (RS)",
		"url": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/4315602",
	},
	{
		"name": "Santa Vitória do Palmar (RS)",
		"url": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/4317103",
	},
]
									  
HEADERS = {
	"User-Agent": (
		"Mozilla/5.0 (X11; Linux x86_64; rv:128.0) "
		"Gecko/20100101 Firefox/128.0 "
		"(Trabalho Academico - Extracao de Conhecimento)"
	),
	"Accept-Language": "pt-BR,pt;q=0.9,en;q=0.5",
}
												 
REQUEST_DELAY_S = 2.0
															
													 
MAPA_CLASSES_ONTOLOGIA = {
								 
	"Animal":	{"termos": []},
	"Mamifero":  {"termos": [
		"mamífero", "mamíferos", "capivara", "capivaras", "graxaim",
		"graxaim-do-campo", "ratão-do-banhado", "lontra", "tatu",
		"gambá", "preá", "cervo", "cervo-do-pantanal", "veado",
		"raposa", "mão-pelada", "furão", "guaxinim", "quati",
		"lobo-guará", "cachorro-do-mato", "zorrilho",
	]},
	"Reptil":	{"termos": [
		"réptil", "répteis", "jacaré", "jacaré-de-papo-amarelo",
		"jacaré-do-papo-amarelo", "tartaruga", "cágado", "cobra",
		"serpente", "serpentes", "lagarto", "lagartos", "teiú",
	]},
	"Ave":	   {"termos": [
		"ave", "aves", "coruja", "coruja-buraqueira", "quero-quero",
		"cisne", "cisne-de-pescoço-negro", "marreca", "garça",
		"gavião", "falcão", "pássaro", "pássaros", "flamingo",
		"colhereiro", "biguá", "socó", "sabiá", "joão-de-barro",
	]},
	"Anfibio":   {"termos": [
		"anfíbio", "anfíbios", "sapo", "perereca",
	]},
										 
	"EspecieAnimal": {"termos": [
		"cerdocyon thous", "caiman latirostris",
		"hydrochoerus hydrochaeris", "athene cunicularia",
		"myocastor coypus", "cygnus melancoryphus",
		"tupinambis merianae", "rhinella", "leptodactylus",
	]},
					 
	"Rodovia": {"termos": [
		"br-471", "br 471", "br471",
	]},
	"TrechoRodoviario": {"termos": [
		"trecho rodoviário", "segmento rodoviário",
	]},
									 
	"EventoAtropelamento": {"termos": [
		"atropelamento", "atropelamentos", "atropelada", "atropelado",
		"atropeladas", "atropelados", "colisão", "roadkill",
	]},
								  
	"CondicaoClimatica": {"termos": [
		"chuva", "precipitação", "temperatura", "vento",
		"clima", "climática", "seca", "umidade", "tempestade",
		"inverno", "verão", "outono", "primavera",
	]},
	"CondicaoLuminosidade": {"termos": [
		"noturno", "noturna", "diurno", "diurna", "crepuscular",
		"crepúsculo", "amanhecer", "anoitecer", "luminosidade",
	]},
					 
	"TipoVegetacao": {"termos": [
		"vegetação", "banhado", "banhados", "campo nativo",
		"restinga", "mata ciliar", "floresta", "macrófita", "macrófitas",
		"juncal", "junco", "vegetação aquática",
	]},
	"CorpoHidrico": {"termos": [
		"lagoa", "lagoas", "arroio", "arroios", "canal",
		"lagoa mirim", "lagoa mangueira", "bacia hidrográfica",
		"recurso hídrico", "curso d'água", "alagado",
	]},
							  
	"FatorAntropico": {"termos": [
		"velocidade", "tráfego", "trânsito", "veículo", "veículos",
		"caminhão", "automóvel", "sinalização", "acostamento",
		"pavimentação", "asfalto",
	]},
	"FatorEcologico": {"termos": [
		"migração", "migratório", "deslocamento", "reprodução",
		"termorregulação", "forrageamento", "dispersão",
		"sazonalidade", "sazonal",
	]},
						 
	"LocalizacaoGeografica": {"termos": [
		"latitude", "longitude", "coordenada", "coordenadas",
		"georreferenciado", "geolocalização", "GPS",
	]},
							  
	"PeriodoTemporal": {"termos": [
		"período sazonal", "período noturno", "período diurno",
		"estação do ano", "semestre", "bimestre",
		"trimestre", "década",
	]},
								 
	"MedidaMitigacao": {"termos": [
		"passagem de fauna", "cerca de proteção", "cercamento",
		"redutor de velocidade", "ecoduto",
		"mitigação", "medida mitigatória",
	]},
}
																			
_INDICE_TERMO_CLASSE: dict[str, str] = {}
for _cls, _info in MAPA_CLASSES_ONTOLOGIA.items():
	for _t in _info["termos"]:
		_INDICE_TERMO_CLASSE[_t.lower()] = _cls
																  
PADROES_RELACAO = {
												  
	"habita":		  "possuiHabitat",
	"habitar":		 "possuiHabitat",
	"vive":			"possuiHabitat",
	"viver":		   "possuiHabitat",
	"ocorre":		  "localizadoEm",
	"ocorrer":		 "localizadoEm",
	"localiza":		"localizadoEm",
	"localizar":	   "localizadoEm",
	"situa":		   "localizadoEm",
	"encontra":		"localizadoEm",
	"atravessa":	   "atravessaHabitat",
	"atravessar":	  "atravessaHabitat",
	"cruza":		   "atravessaHabitat",
	"cruzar":		  "atravessaHabitat",
	"corta":		   "atravessaHabitat",
	"secciona":		"atravessaHabitat",
	"intercepta":	  "atravessaHabitat",
	"atropela":		"envolveAnimal",
	"atropelar":	   "envolveAnimal",
	"atropelado":	  "envolveAnimal",
	"atropelada":	  "envolveAnimal",
	"pertence":		"pertenceAEspecie",
	"pertencer":	   "pertenceAEspecie",
	"classificado":	"pertenceAEspecie",
	"migra":		   "temFatorRisco",
	"migrar":		  "temFatorRisco",
	"desloca":		 "temFatorRisco",
	"reproduz":		"temFatorRisco",
	"protege":		 "mitigadoPor",
	"proteger":		"mitigadoPor",
	"reduz":		   "mitigadoPor",
	"reduzir":		 "mitigadoPor",
	"mitiga":		  "mitigadoPor",
	"mitigar":		 "mitigadoPor",
	"compõe":		  "compostoPorTrechos",
	"compor":		  "compostoPorTrechos",
	"possui":		  "possuiHabitat",
	"adjacente":	   "adjacenteA",
	"próximo":		 "adjacenteA",
}
																			  
					 
																			  
@dataclass
class FonteTexto:
	url: str
	titulo: str = ""
	texto_bruto: str = ""
	paragrafos: list[str] = field(default_factory=list)
	status_code: int = 0
	erro: Optional[str] = None
@dataclass
class EntidadeExtraida:
	texto: str
	label_spacy: str													  
	classe_ontologia: str									
	inicio: int = 0							   
	fim: int = 0
	confianca: float = 0.0										 
@dataclass
class TriplaExtraida:
	entidade1: str
	relacao: str
	entidade2: str
	classe_entidade1: str = ""
	classe_entidade2: str = ""
	propriedade_ontologia: str = ""
	sentenca_origem: str = ""
	fonte_url: str = ""
	metodo_extracao: str = ""												  
																			  
							  
																			  
class ScraperTaim:
	def __init__(self, headers: dict = HEADERS, delay: float = REQUEST_DELAY_S):
		self.session = requests.Session()
		self.session.headers.update(headers)
		self.delay = delay
		self._ultimo_request: float = 0.0
	def _respeitar_delay(self) -> None:
		elapsed = time.time() - self._ultimo_request
		if elapsed < self.delay:
			wait = self.delay - elapsed
			print(f"Aguardando {wait:.1f}s (politeness delay)")
			time.sleep(wait)
	def buscar_pagina(self, url: str, timeout: int = 15) -> FonteTexto:
		fonte = FonteTexto(url=url)
		try:
			self._respeitar_delay()
			print(f"GET {url}")
			response = self.session.get(url, timeout=timeout, allow_redirects=True)
			self._ultimo_request = time.time()
			response.raise_for_status()
			fonte.status_code = response.status_code
															   
			if response.encoding and "iso" in response.encoding.lower():
				response.encoding = "utf-8"
			fonte.texto_bruto = response.text
			print(
				f"  OK {response.status_code} - "
				f"{len(response.text):,} caracteres recebidos"
			)
		except requests.exceptions.ConnectionError as e:
			fonte.erro = f"Falha de conexão: {e}"
			print(f"  ERRO ConnectionError em {url}: {e}")
		except requests.exceptions.Timeout as e:
			fonte.erro = f"Timeout ({timeout}s): {e}"
			print(f"  ERRO Timeout em {url}: {e}")
		except requests.exceptions.HTTPError as e:
			fonte.status_code = response.status_code
			fonte.erro = f"HTTP {response.status_code}: {e}"
			print(f"  ERRO HTTPError {response.status_code} em {url}")
		except requests.exceptions.TooManyRedirects as e:
			fonte.erro = f"Excesso de redirecionamentos: {e}"
			print(f"  ERRO TooManyRedirects em {url}")
		except requests.exceptions.ContentDecodingError as e:
			fonte.erro = f"Erro de decodificação: {e}"
			print(f"  ERRO ContentDecodingError em {url}")
		except requests.exceptions.RequestException as e:
			fonte.erro = f"Erro genérico de requisição: {e}"
			print(f"  ERRO RequestException em {url}: {e}")
		return fonte
	def parse_wikipedia(self, fonte: FonteTexto) -> FonteTexto:
		if fonte.erro or not fonte.texto_bruto:
			return fonte
		try:
			soup = BeautifulSoup(fonte.texto_bruto, "html.parser")
							
			titulo_tag = soup.find("h1", {"id": "firstHeading"})
			if titulo_tag:
				fonte.titulo = titulo_tag.get_text(strip=True)
			else:
									   
				title_tag = soup.find("title")
				fonte.titulo = title_tag.get_text(strip=True) if title_tag else "Sem título"
										 
			content_div = soup.find("div", {"id": "mw-content-text"})
			if not content_div:
				content_div = soup.find("div", {"class": "mw-parser-output"})
			if not content_div:
				fonte.erro = "Não foi possível localizar o conteúdo do artigo"
				print(f"  AVISO Conteúdo não encontrado em {fonte.url}")
				return fonte
										   
			seletores_remover = [
				"table",										   
				"div.navbox",									   
				"div.reflist",									   
				"div.reference",								   
				"sup.reference",								
				"span.mw-editsection",						 
				"div.thumb",							   
				"div.toc",							 
				"div.noprint",											
				"div.metadata",						   
				"div.sistersitebox",							
				"div.hatnote",										 
				"div.mw-empty-elt",							  
				"script", "style",								
				"figure",							   
				"div.refbegin",							   
			]
			for seletor in seletores_remover:
				for elem in content_div.select(seletor):
					elem.decompose()
									   
			paragrafos = []
			for p in content_div.find_all(["p", "li"]):
				texto = p.get_text(separator=" ", strip=True)
															 
				texto = re.sub(r"\[\d+\]", "", texto)							
				texto = re.sub(r"\s{2,}", " ", texto)						 
				texto = texto.strip()
				if len(texto) > 30:									  
					paragrafos.append(texto)
			fonte.paragrafos = paragrafos
			print(
				f"  OK Wikipedia parseada: '{fonte.titulo}' - "
				f"{len(paragrafos)} parágrafos extraídos"
			)
		except Exception as e:
			fonte.erro = f"Erro no parsing HTML: {e}"
			print(f"  ERRO Erro ao parsear {fonte.url}: {e}")
		return fonte
	def parse_artigo_cientifico(self, fonte: FonteTexto) -> FonteTexto:
		if fonte.erro or not fonte.texto_bruto:
			return fonte
		try:
			soup = BeautifulSoup(fonte.texto_bruto, "html.parser")
							
			titulo_tag = (
				soup.find("h1", class_=re.compile(r"article", re.I))
				or soup.find("h1")
				or soup.find("title")
			)
			fonte.titulo = titulo_tag.get_text(strip=True) if titulo_tag else "Artigo sem título"
																	  
			seletores_corpo = [
				"div.articleBody",							   
				"div#articleText",								 
				"article",										   
				"div.article-body",								 
				"div#content",								
				"div.main-content",						   
				"div.article-content",						
				"div.abstract",										  
				"section",								  
			]
			corpo = None
			for seletor in seletores_corpo:
				corpo = soup.select_one(seletor)
				if corpo:
					print(f"  Corpo encontrado via seletor: {seletor}")
					break
			if not corpo:
											
				corpo = soup.find("body")
				if not corpo:
					fonte.erro = "Corpo do artigo não localizado"
					print(f"  AVISO Corpo não encontrado em {fonte.url}")
					return fonte
											   
			for tag in corpo.select("nav, header, footer, script, style, aside"):
				tag.decompose()
			paragrafos = []
			for elem in corpo.find_all(["p", "li", "div"]):
														   
				if elem.name == "div" and elem.find("div"):
					continue
				texto = elem.get_text(separator=" ", strip=True)
				texto = re.sub(r"\s{2,}", " ", texto).strip()
				if len(texto) > 40:
					paragrafos.append(texto)
																			 
			paragrafos_unicos = list(dict.fromkeys(paragrafos))
			fonte.paragrafos = paragrafos_unicos
			print(
				f"  OK Artigo parseado: '{fonte.titulo[:60]}...' - "
				f"{len(paragrafos_unicos)} parágrafos"
			)
		except Exception as e:
			fonte.erro = f"Erro no parsing do artigo: {e}"
			print(f"  ERRO Erro ao parsear artigo {fonte.url}: {e}")
		return fonte
	def coletar_wikidata(self) -> list[FonteTexto]:
		fontes: list[FonteTexto] = []
		print("\n  --- Wikidata (SPARQL) ---")
		for q in WIKIDATA_QUERIES:
			print(f"  Consultando Wikidata: {q['name']}")
			try:
				self._respeitar_delay()
				r = self.session.get(
					WIKIDATA_SPARQL_ENDPOINT,
					params={"query": q["query"], "format": "json"},
					headers={"Accept": "application/sparql-results+json"},
					timeout=30,
				)
				self._ultimo_request = time.time()
				if r.status_code == 200:
					data = r.json()
					bindings = data.get("results", {}).get("bindings", [])
					if bindings:
						paragrafos = []
						for row in bindings:
							label = row.get("itemLabel", {}).get("value", "")
							status = row.get("statusLabel", {}).get("value", "")
							habitat = row.get("habitatLabel", {}).get("value", "")
																			
							partes = [f"A espécie {q['name']} ({label})"]
							if status:
								partes.append(
									f"possui status de conservação IUCN: {status}"
								)
							if habitat:
								partes.append(f"habita {habitat}")
							partes.append(
								"e é encontrada na região da Estação "
								"Ecológica do Taim, onde está sujeita a "
								"atropelamento na rodovia BR-471"
							)
							paragrafos.append(". ".join(partes) + ".")
						fonte = FonteTexto(
							url=f"wikidata:sparql:{q['name']}",
							titulo=f"Wikidata - {q['name']}",
							paragrafos=paragrafos,
							status_code=200,
						)
						fontes.append(fonte)
						print(
							f"	OK {len(bindings)} resultado(s), "
							f"{len(paragrafos)} parágrafos gerados"
						)
					else:
						print(f"	AVISO Sem resultados para {q['name']}")
				elif r.status_code == 429:
					print("	AVISO Rate limited (429), pulando query")
				else:
					print(f"	ERRO HTTP {r.status_code}")
			except Exception as e:
				print(f"	ERRO Erro Wikidata ({q['name']}): {e}")
		return fontes
	def coletar_ibge(self) -> list[FonteTexto]:
		fontes: list[FonteTexto] = []
		print("\n  --- IBGE API (Localidades) ---")
		for item in IBGE_API_URLS:
			print(f"  Consultando IBGE: {item['name']}")
			try:
				self._respeitar_delay()
				r = self.session.get(item["url"], timeout=15)
				self._ultimo_request = time.time()
				if r.status_code == 200:
					data = r.json()
					nome_mun = data.get("nome", "")
					micro = data.get("microrregiao", {})
					meso = micro.get("mesorregiao", {})
					uf = meso.get("UF", {})
					regiao_im = data.get("regiao-imediata", {})
					paragrafos = [
						f"O município de {nome_mun} está localizado no "
						f"estado {uf.get('nome', 'RS')}, na microrregião "
						f"de {micro.get('nome', '')}, mesorregião "
						f"{meso.get('nome', '')}.",
						f"{nome_mun} pertence à região imediata de "
						f"{regiao_im.get('nome', '')} e encontra-se na "
						f"área de influência da Estação Ecológica do Taim, "
						f"sendo atravessado pela rodovia BR-471 que "
						f"intercepta habitats de banhado e lagoas.",
						f"A localização geográfica de {nome_mun} no "
						f"bioma Pampa o torna relevante para o estudo "
						f"de atropelamento de fauna silvestre na região "
						f"do Banhado do Taim.",
					]
					fonte = FonteTexto(
						url=item["url"],
						titulo=f"IBGE - {item['name']}",
						paragrafos=paragrafos,
						status_code=200,
					)
					fontes.append(fonte)
					print(
						f"	OK Município: {nome_mun}, "
						f"{len(paragrafos)} parágrafos gerados"
					)
				else:
					print(f"	ERRO HTTP {r.status_code}")
			except Exception as e:
				print(f"	ERRO Erro IBGE ({item['name']}): {e}")
		return fontes
	def coletar_todas_fontes(self) -> list[FonteTexto]:
		fontes: list[FonteTexto] = []
		print("=== ETAPA 1: COLETA DE FONTES (MULTIMODAL) ===")
									
		print("\n  --- Wikipedia (scraping HTML) ---")
		for url in URLS_WIKIPEDIA:
			fonte = self.buscar_pagina(url)
			fonte = self.parse_wikipedia(fonte)
			fontes.append(fonte)
											  
		print("\n  --- Artigos Científicos ---")
		for url in URLS_ARTIGOS:
			fonte = self.buscar_pagina(url)
			fonte = self.parse_artigo_cientifico(fonte)
			fontes.append(fonte)
														   
		print("\n  --- Portais de Notícias Ambientais ---")
		for url in URLS_NOTICIAS:
			fonte = self.buscar_pagina(url)
			fonte = self.parse_artigo_cientifico(fonte)
			fontes.append(fonte)
											
		fontes_wikidata = self.coletar_wikidata()
		fontes.extend(fontes_wikidata)
								   
		fontes_ibge = self.coletar_ibge()
		fontes.extend(fontes_ibge)
		sucesso = sum(1 for f in fontes if not f.erro and f.paragrafos)
		falha   = sum(1 for f in fontes if f.erro or not f.paragrafos)
		print(f"\n  Fontes coletadas: {sucesso} sucesso, {falha} falha(s)")
		print(f"  Detalhamento por tipo:")
		print(f"	Wikipedia:	 {sum(1 for f in fontes if 'wikipedia.org' in f.url and f.paragrafos)}")
		print(f"	Artigos:	   {sum(1 for f in fontes if 'periodicos' in f.url or 'scielo' in f.url)}")
		print(f"	Notícias:	  {sum(1 for f in fontes if 'g1.globo' in f.url or 'oeco' in f.url)}")
		print(f"	Wikidata:	  {len(fontes_wikidata)}")
		print(f"	IBGE:		  {len(fontes_ibge)}")
		return fontes
																			  
									   
																			  
class ProcessadorNLP:
	def __init__(self, modelo: str = "pt_core_news_sm"):
		print("=== ETAPA 2: INICIALIZACAO DO PIPELINE NLP ===")
		try:
			self.nlp = spacy.load(modelo)
			print(f"  OK Modelo spaCy carregado: {modelo}")
			print(f"	Pipeline: {self.nlp.pipe_names}")
		except OSError:
			print(
				f"  ERRO Modelo '{modelo}' não encontrado. "
				f"Execute: python -m spacy download {modelo}"
			)
			raise SystemExit(1)
														  
		self.nlp.max_length = 2_000_000
																
		self._configurar_entity_ruler()
	def _configurar_entity_ruler(self) -> None:
		try:
			ruler = self.nlp.add_pipe("entity_ruler", before="ner")
		except ValueError:
											 
			ruler = self.nlp.get_pipe("entity_ruler")
		patterns = [
								  
			{"label": "LOC", "pattern": [{"TEXT": {"REGEX": r"^BR-?\d{2,3}$"}}]},
									   
			{"label": "LOC", "pattern": [
				{"LOWER": "estação"}, {"LOWER": "ecológica"},
				{"LOWER": "do"}, {"LOWER": "taim"},
			]},
			{"label": "LOC", "pattern": [
				{"LOWER": "esec"}, {"LOWER": "taim"},
			]},
			{"label": "LOC", "pattern": [
				{"LOWER": "banhado"}, {"LOWER": "do"}, {"LOWER": "taim"},
			]},
					
			{"label": "LOC", "pattern": [
				{"LOWER": "lagoa"}, {"LOWER": "mirim"},
			]},
			{"label": "LOC", "pattern": [
				{"LOWER": "lagoa"}, {"LOWER": "mangueira"},
			]},
												  
			{"label": "MISC", "pattern": [
				{"SHAPE": "Xxxxx"}, {"SHAPE": "xxxx"},
				{"IS_ALPHA": True, "LENGTH": {">=": 4}},
			]},
		]
		ruler.add_patterns(patterns)
		print(f"	EntityRuler configurado com {len(patterns)} padrões")
	def processar_texto(self, texto: str) -> Doc:
		try:
			return self.nlp(texto)
		except Exception as e:
			print(f"Erro ao processar texto com spaCy: {e}")
			return self.nlp("")						   
	def extrair_entidades(
		self, doc: Doc, url_fonte: str = ""
	) -> list[EntidadeExtraida]:
		entidades: list[EntidadeExtraida] = []
		textos_vistos: set[str] = set()
													
		for ent in doc.ents:
			texto_norm = ent.text.strip().lower()
													
			if texto_norm in textos_vistos or len(texto_norm) < 3:
				continue
			if texto_norm in self._STOPWORDS_TRIPLA:
				continue
			textos_vistos.add(texto_norm)
			classe = self._mapear_classe(texto_norm)
			entidades.append(EntidadeExtraida(
				texto=ent.text.strip(),
				label_spacy=ent.label_,
				classe_ontologia=classe,
				inicio=ent.start_char,
				fim=ent.end_char,
				confianca=0.8 if classe else 0.4,
			))
																 
		texto_lower = doc.text.lower()
		for termo, classe in _INDICE_TERMO_CLASSE.items():
			if termo in textos_vistos:
				continue
															
			pattern = r"\b" + re.escape(termo) + r"\b"
			match = re.search(pattern, texto_lower)
			if match:
				textos_vistos.add(termo)
				entidades.append(EntidadeExtraida(
					texto=termo,
					label_spacy="DOMAIN",
					classe_ontologia=classe,
					inicio=match.start(),
					fim=match.end(),
					confianca=0.9,								   
				))
		return entidades
																		
	_STOPWORDS_TRIPLA = frozenset({
		"que", "qual", "quais", "onde", "como", "quando", "se", "isso",
		"isto", "ele", "ela", "eles", "elas", "seu", "sua", "seus",
		"suas", "este", "esta", "esse", "essa", "aquele", "aquela",
		"o", "a", "os", "as", "um", "uma", "uns", "umas",
		"de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas",
		"por", "para", "com", "sem", "sob", "sobre",
		"já", "mais", "muito", "bem", "também", "ainda", "só",
		"não", "sim", "há", "ter", "ser", "estar", "ir",
		"km", "ano", "mês", "área", "região", "parte",
	})
	def _mapear_classe(self, texto: str) -> str:
		texto_l = texto.lower().strip()
								  
		if texto_l in self._STOPWORDS_TRIPLA or len(texto_l) < 3:
			return ""
					 
		if texto_l in _INDICE_TERMO_CLASSE:
			return _INDICE_TERMO_CLASSE[texto_l]
																
																	
																 
													   
		for termo, classe in _INDICE_TERMO_CLASSE.items():
			if len(termo) < 5:
				continue								
			pattern = r"\b" + re.escape(termo) + r"\b"
			if re.search(pattern, texto_l):
				return classe
		return ""
	def extrair_triplas_dependencia(
		self, doc: Doc, url_fonte: str = ""
	) -> list[TriplaExtraida]:
		triplas: list[TriplaExtraida] = []
		for sent in doc.sents:
			for token in sent:
															 
				if token.pos_ not in ("VERB", "AUX", "ADJ"):
					continue
				lemma = token.lemma_.lower()
				text_lower = token.text.lower()
																   
				prop_ontologia = (
					PADROES_RELACAO.get(lemma, "")
					or PADROES_RELACAO.get(text_lower, "")
				)
													 
				sujeitos = [
					child for child in token.children
					if child.dep_ in ("nsubj", "nsubj:pass")
				]
														  
				objetos = [
					child for child in token.children
					if child.dep_ in ("obj", "obl", "xcomp", "acomp", "nmod")
				]
				for subj in sujeitos:
					subj_span = self._expandir_span(subj, doc)
																	
					if subj_span.lower().strip() in self._STOPWORDS_TRIPLA:
						continue
					if len(subj_span.strip()) < 3:
						continue
					for obj in objetos:
						obj_span = self._expandir_span(obj, doc)
												  
						if obj_span.lower().strip() in self._STOPWORDS_TRIPLA:
							continue
						if len(obj_span.strip()) < 3:
							continue
											   
						cls_s = self._mapear_classe(subj_span)
						cls_o = self._mapear_classe(obj_span)
															  
																 
																
						if not cls_s or not cls_o:
							continue
											
						relacao = prop_ontologia if prop_ontologia else lemma
						tripla = TriplaExtraida(
							entidade1=subj_span,
							relacao=relacao,
							entidade2=obj_span,
							classe_entidade1=cls_s,
							classe_entidade2=cls_o,
							propriedade_ontologia=prop_ontologia,
							sentenca_origem=sent.text.strip()[:200],
							fonte_url=url_fonte,
							metodo_extracao="dep_parse",
						)
						triplas.append(tripla)
		return triplas
	def extrair_triplas_coocorrencia(
		self, doc: Doc, url_fonte: str = ""
	) -> list[TriplaExtraida]:
		triplas: list[TriplaExtraida] = []
														   
		mapa_coocorrencia = {
			("Mamifero",  "TipoVegetacao"):		  "possuiHabitat",
			("Mamifero",  "CorpoHidrico"):			"possuiHabitat",
			("Reptil",	"TipoVegetacao"):		   "possuiHabitat",
			("Reptil",	"CorpoHidrico"):			"possuiHabitat",
			("Ave",	   "TipoVegetacao"):		   "possuiHabitat",
			("Ave",	   "CorpoHidrico"):			"possuiHabitat",
			("Anfibio",   "TipoVegetacao"):		   "possuiHabitat",
			("Anfibio",   "CorpoHidrico"):			"possuiHabitat",
			("Rodovia",   "TipoVegetacao"):		   "atravessaHabitat",
			("Rodovia",   "CorpoHidrico"):			"atravessaHabitat",
			("TrechoRodoviario", "TipoVegetacao"):	"atravessaHabitat",
			("TrechoRodoviario", "CorpoHidrico"):	 "atravessaHabitat",
			("EventoAtropelamento", "Mamifero"):	   "envolveAnimal",
			("EventoAtropelamento", "Reptil"):		 "envolveAnimal",
			("EventoAtropelamento", "Ave"):			"envolveAnimal",
			("EventoAtropelamento", "Anfibio"):		"envolveAnimal",
			("EventoAtropelamento", "Rodovia"):		"ocorreEmRodovia",
			("EventoAtropelamento", "CondicaoClimatica"): "temCondicaoAmbiental",
			("EventoAtropelamento", "PeriodoTemporal"): "ocorreDurantePeriodo",
			("FatorAntropico", "MedidaMitigacao"):	 "mitigadoPor",
			("FatorEcologico", "MedidaMitigacao"):	 "mitigadoPor",
		}
		for sent in doc.sents:
			sent_text = sent.text.lower()
																   
			entidades_sent: list[tuple[str, str]] = []				   
			for termo, classe in _INDICE_TERMO_CLASSE.items():
				if re.search(r"\b" + re.escape(termo) + r"\b", sent_text):
					entidades_sent.append((termo, classe))
										 
			for i, (txt_a, cls_a) in enumerate(entidades_sent):
				for txt_b, cls_b in entidades_sent[i + 1:]:
					if cls_a == cls_b:
						continue								 
											   
					rel = (
						mapa_coocorrencia.get((cls_a, cls_b))
						or mapa_coocorrencia.get((cls_b, cls_a))
					)
					if rel:
																		 
						if (cls_a, cls_b) in mapa_coocorrencia:
							e1, c1, e2, c2 = txt_a, cls_a, txt_b, cls_b
						else:
							e1, c1, e2, c2 = txt_b, cls_b, txt_a, cls_a
						triplas.append(TriplaExtraida(
							entidade1=e1,
							relacao=rel,
							entidade2=e2,
							classe_entidade1=c1,
							classe_entidade2=c2,
							propriedade_ontologia=rel,
							sentenca_origem=sent.text.strip()[:200],
							fonte_url=url_fonte,
							metodo_extracao="coocorrencia",
						))
		return triplas
	def _expandir_span(self, token, doc: Doc) -> str:
		tokens_span = [token]
		for child in token.children:
																	  
			if child.dep_ in ("amod", "compound", "flat", "flat:name", "nmod", "appos"):
				if child.pos_ not in ("DET", "ADP"):
					tokens_span.append(child)
													  
					for grandchild in child.children:
						if grandchild.dep_ in ("amod", "flat") and grandchild.pos_ not in ("DET", "ADP"):
							tokens_span.append(grandchild)
									  
		tokens_span.sort(key=lambda t: t.i)
		texto = " ".join(t.text for t in tokens_span).strip()
																			
		texto = re.sub(r"(?i)^(o|a|os|as|um|uma|uns|umas|de|da|do|das|dos|em|na|no|nas|nos|à|ao|às|aos)\s+", "", texto)
		return texto
																			  
									 
																			  
class ConsolidadorResultados:
	def __init__(self, dir_saida: str = "resultados_extracao"):
		self.dir_saida = Path(dir_saida)
		self.dir_saida.mkdir(parents=True, exist_ok=True)
	def deduplicar_triplas(
		self, triplas: list[TriplaExtraida]
	) -> list[TriplaExtraida]:
		vistas: dict[tuple, TriplaExtraida] = {}
		for t in triplas:
			chave = (
				t.entidade1.lower().strip(),
				t.relacao.lower().strip(),
				t.entidade2.lower().strip(),
			)
			if chave not in vistas:
				vistas[chave] = t
		dedup = list(vistas.values())
		print(f"  Deduplicação: {len(triplas)} → {len(dedup)} triplas únicas")
		return dedup
	def filtrar_triplas_relevantes(
		self, triplas: list[TriplaExtraida]
	) -> list[TriplaExtraida]:
		relevantes = [
			t for t in triplas
			if t.classe_entidade1 or t.classe_entidade2
		]
		print(
			f"  Filtragem: {len(relevantes)} triplas com mapeamento ontológico "
			f"(de {len(triplas)} totais)"
		)
		return relevantes
	def exportar_json(
		self,
		entidades: list[EntidadeExtraida],
		triplas: list[TriplaExtraida],
		fontes: list[FonteTexto],
	) -> Path:
		caminho = self.dir_saida / "conhecimento_extraido.json"
		dados = {
			"metadados": {
				"dominio": "Banhado do Taim - Atropelamento de Fauna",
				"ontologia_iri": "http://www.semanticweb.org/ontologias/"
								 "banhado-do-taim/atropelamento-fauna",
				"total_fontes": len(fontes),
				"fontes_sucesso": sum(1 for f in fontes if not f.erro),
				"total_entidades": len(entidades),
				"total_triplas": len(triplas),
			},
			"fontes": [
				{
					"url": f.url,
					"titulo": f.titulo,
					"paragrafos_extraidos": len(f.paragrafos),
					"erro": f.erro,
				}
				for f in fontes
			],
			"entidades": [asdict(e) for e in entidades],
			"triplas": [asdict(t) for t in triplas],
		}
		try:
			with open(caminho, "w", encoding="utf-8") as fp:
				json.dump(dados, fp, ensure_ascii=False, indent=2)
			print(f"  OK JSON exportado: {caminho}")
		except IOError as e:
			print(f"  ERRO Erro ao salvar JSON: {e}")
		return caminho
	def exportar_csv_triplas(self, triplas: list[TriplaExtraida]) -> Path:
		caminho = self.dir_saida / "triplas_extraidas.csv"
		try:
			with open(caminho, "w", encoding="utf-8", newline="") as fp:
				writer = csv.DictWriter(fp, fieldnames=[
					"entidade1", "relacao", "entidade2",
					"classe_entidade1", "classe_entidade2",
					"propriedade_ontologia", "metodo_extracao",
					"fonte_url", "sentenca_origem",
				])
				writer.writeheader()
				for t in triplas:
					writer.writerow(asdict(t))
			print(f"  OK CSV exportado: {caminho}")
		except IOError as e:
			print(f"  ERRO Erro ao salvar CSV: {e}")
		return caminho
	def exibir_resumo(
		self,
		entidades: list[EntidadeExtraida],
		triplas: list[TriplaExtraida],
	) -> None:
		print("\n=== RESUMO DA EXTRACAO DE CONHECIMENTO ===")
										   
		classes_contagem: dict[str, int] = {}
		for e in entidades:
			cls = e.classe_ontologia if e.classe_ontologia else "(sem mapeamento)"
			classes_contagem[cls] = classes_contagem.get(cls, 0) + 1
		print(f"\n  ENTIDADES EXTRAÍDAS: {len(entidades)}")
		print("  ----------------------------------------")
		for cls, n in sorted(classes_contagem.items(), key=lambda x: -x[1]):
			barra = "*" * min(n, 30)
			print(f"	{cls:<28s} {n:>4d}  {barra}")
										 
		relacoes_contagem: dict[str, int] = {}
		metodos_contagem: dict[str, int] = {}
		for t in triplas:
			rel = t.propriedade_ontologia if t.propriedade_ontologia else t.relacao
			relacoes_contagem[rel] = relacoes_contagem.get(rel, 0) + 1
			metodos_contagem[t.metodo_extracao] = metodos_contagem.get(t.metodo_extracao, 0) + 1
		print(f"\n  TRIPLAS EXTRAÍDAS: {len(triplas)}")
		print("  ----------------------------------------")
		print("  Por relação ontológica:")
		for rel, n in sorted(relacoes_contagem.items(), key=lambda x: -x[1]):
			print(f"	{rel:<30s} {n:>4d}")
		print("\n  Por método de extração:")
		for met, n in sorted(metodos_contagem.items(), key=lambda x: -x[1]):
			print(f"	{met:<30s} {n:>4d}")
									 
		print(f"\n  EXEMPLOS DE TRIPLAS (primeiras 15):")
		print("  ----------------------------------------")
		for i, t in enumerate(triplas[:15], 1):
			cls1 = f"[{t.classe_entidade1}]" if t.classe_entidade1 else ""
			cls2 = f"[{t.classe_entidade2}]" if t.classe_entidade2 else ""
			print(f"	{i:>2d}. ({t.entidade1} {cls1},  "
				  f"{t.relacao},  "
				  f"{t.entidade2} {cls2})")
		print("\n" + "=" * 70)
																			  
					
																			  
def executar_pipeline() -> None:
	print("=== EXTRACAO DE CONHECIMENTO - BANHADO DO TAIM ===")
							 
	scraper = ScraperTaim()
	fontes = scraper.coletar_todas_fontes()
	fontes_validas = [f for f in fontes if f.paragrafos]
	if not fontes_validas:
		print("Nenhuma fonte válida coletada. Abortando.")
		return
										
	nlp = ProcessadorNLP()
	todas_entidades: list[EntidadeExtraida] = []
	todas_triplas: list[TriplaExtraida] = []
	print("=== ETAPA 3: EXTRACAO DE ENTIDADES E RELACOES ===")
	for fonte in fontes_validas:
		print(f"\n  Processando: {fonte.titulo}")
		print(f"  URL: {fonte.url}")
																 
		texto_completo = "\n".join(fonte.paragrafos)
														
		if len(texto_completo) > 500_000:
			texto_completo = texto_completo[:500_000]
			print(f"  AVISO Texto truncado para 500K caracteres")
		doc = nlp.processar_texto(texto_completo)
						   
		entidades = nlp.extrair_entidades(doc, url_fonte=fonte.url)
		todas_entidades.extend(entidades)
		print(f"	→ {len(entidades)} entidades extraídas")
													
		triplas_dep = nlp.extrair_triplas_dependencia(doc, url_fonte=fonte.url)
		todas_triplas.extend(triplas_dep)
		print(f"	→ {len(triplas_dep)} triplas (análise de dependência)")
										   
		triplas_cooc = nlp.extrair_triplas_coocorrencia(doc, url_fonte=fonte.url)
		todas_triplas.extend(triplas_cooc)
		print(f"	→ {len(triplas_cooc)} triplas (co-ocorrência)")
								   
	print("=== ETAPA 4: CONSOLIDACAO E EXPORTACAO ===")
	consolidador = ConsolidadorResultados()
						  
	triplas_unicas = consolidador.deduplicar_triplas(todas_triplas)
	triplas_relevantes = consolidador.filtrar_triplas_relevantes(triplas_unicas)
			  
	consolidador.exportar_json(todas_entidades, triplas_relevantes, fontes)
	consolidador.exportar_csv_triplas(triplas_relevantes)
				  
	consolidador.exibir_resumo(todas_entidades, triplas_relevantes)
	print("\n  Pipeline concluído com sucesso.")
																			  
		  
																			  
if __name__ == "__main__":
	executar_pipeline()

