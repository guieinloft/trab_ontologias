# 1. Introdução e Contexto
O Banhado do Taim, localizado no Rio Grande do Sul, é um dos ecossistemas úmidos mais vitais do Brasil, caracterizado por sua extensa biodiversidade. A rodovia BR-471 cruza longitudinalmente essa região de banhados, originando um preocupante índice de atropelamentos de fauna silvestre. As informações ambientais e ecológicas que descrevem essa dinâmica — dados sobre espécies nativas, condições climáticas em tempo real, tipos de habitats intersectados e variáveis logísticas rodoviárias — geralmente encontram-se não estruturadas e descentralizadas, dificultando o monitoramento e o embasamento de ações corretivas.

Neste cenário, a Inteligência Artificial Simbólica, por meio do desenvolvimento de Ontologias, provê um mecanismo resoluto para modelar e integrar formalmente o conhecimento do domínio. A representação semântica através de grafos de conhecimento permite organizar os dados ecológicos e viários de forma interoperável. Dessa maneira, sistemas de monitoramento computadorizados podem inferir logicamente novas informações operacionais, cruzar relações complexas entre as entidades observadas e apoiar decisores na implementação assertiva de medidas mitigatórias (e.g., ecodutos, redutores de velocidade e cercamentos direcionadores).

# 2. Modelagem da Ontologia

## Estrutura Base
A ontologia foi idealizada e desenvolvida em OWL (*Web Ontology Language*) e o esquema da sua *TBox* foi parametrizado inteiramente via Python (`owlready2`). A arquitetura engloba superclasses principais que refletem o domínio espacial, de fauna e de infraestrutura.

**Classes Principais**
| Superclasse | Subclasses Relevantes |
|---|---|
| `Animal` | `Mamifero`, `Reptil`, `Ave`, `Anfibio` |
| `CaracteristicaHabitat` | `TipoVegetacao`, `CorpoHidrico` |
| `CondicaoAmbiental` | `CondicaoClimatica`, `CondicaoLuminosidade` |
| `FatorRisco` | `FatorAntropico`, `FatorEcologico` |
| *Outras Abstratas* | `EventoAtropelamento`, `TrechoRodoviario`, `EspecieAnimal`, `MedidaMitigacao`, `Rodovia` |

**Object Properties (Destaques)**
| Propriedade | Domínio | Alcance |
|---|---|---|
| `possuiHabitat` | `Animal`, `EspecieAnimal` | `CaracteristicaHabitat` |
| `atravessaHabitat` | `Rodovia`, `TrechoRodoviario` | `CaracteristicaHabitat` |
| `envolveAnimal` | `EventoAtropelamento` | `Animal` |
| `ocorreEmTrecho` | `EventoAtropelamento` | `TrechoRodoviario` |
| `mitigadoPor` | `FatorRisco`, `TrechoRodoviario`, `EventoAtropelamento` | `MedidaMitigacao` |

**Data Properties (Destaques)**
| Propriedade | Domínio | Tipo de Dado (Alcance) |
|---|---|---|
| `nomeCientifico` | `EspecieAnimal` | `str` |
| `volumeMedioTrafego` | `TrechoRodoviario` | `int` |
| `temperaturaRegistrada` | `CondicaoClimatica` | `float` |
| `condicaoAnimalPosEvento`| `EventoAtropelamento` | `str` |

## Relações Espaciais e Temporais
A representação das dimensões de espaço e de tempo é imperativa para mapear acidentes de fauna:
- **Relacionamentos Espaciais:** A propriedade de objeto `localizadoEm` conecta os eventos diretamente a uma instância da classe genérica `LocalizacaoGeografica` (cujas *Data Properties* armazenam precisamente as coordenadas flutuantes `coordenadaLatitude` e `coordenadaLongitude`). A topologia ambiental e humana também se manifesta por conexões como `atravessaHabitat` (rodovia secionando um ecossistema) e `adjacenteA`.
- **Relacionamentos Temporais:** Os eventos estão restritos semanticamente a instâncias de `PeriodoTemporal` através da propriedade `ocorreDurantePeriodo` (diferenciando noite, dia e estações). A precisão do registro do momento da colisão é encapsulada pelas propriedades de dados explícitas `dataEvento` e `horaEvento` na classe central de `EventoAtropelamento`.

## Justificativas Lógicas de Modelagem
- **Aplicação de Propriedades Funcionais:** Definiram-se propriedades como `ocorreEmRodovia`, `ocorreEmTrecho` e `ocorreDurantePeriodo` sob o rótulo formal de *FunctionalProperty*. Esta limitação semântica certifica lógicamente que um único fato restrito (o acidente) só se deu materialmente em um rodovia exclusiva, num quilômetro delimitado específico, e em um horário exato, bloqueando inserções espúrias.
- **Modelagem Taxonômica Isolada:** A inclusão da superclasse de suporte taxonômico `EspecieAnimal` (acoplada à classe `Animal` pelo predicado `pertenceAEspecie`) não é acidental; ela previne redundância extrema. Esse *design* consolida os registros biológicos abarcadores (como `statusConservacao` - ex. "Vulnerável") desvinculando-os dos espécimes em campo (os animais concretos envolvidos nas batidas).

## Alternativas Descartadas
1. **Reclusão de Atributos Espaciais e Temporais no próprio Evento:** Estudou-se a viabilidade de modelar características numéricas simples (`latitude`, `longitude`, `hora`) e rótulos (`primavera`) embutidos como vulgares *Data Properties* em `EventoAtropelamento`. *Recusada:* O acoplamento estático limitaria enormemente o reuso lógico. Ao instituir as superclasses modulares `LocalizacaoGeografica` e `PeriodoTemporal`, confere-se expressividade para permitir que outras entidades também possam requerer localização ou janelas de tempo sem repetir metadados estruturais.
2. **Subtipagem Profunda para Eventos:** Analisou-se particionar a classe-mãe em classes-filhas ultraespecíficas (`AtropelamentoMamifero`, `AtropelamentoRépteisNoturnos`, etc.). *Recusada:* Causaria uma inevitável explosão combinatória e manutenção inflexível de restrições. Concentraram-se os eixos hierárquicos essencialmente no nó dos Fatores (`FatorRisco`) e Organismos (`Animal`), vinculando instâncias de um Evento neutro mediante as *Object Properties*.

# 3. Fontes de Informação e Povoamento

## Pipeline de Coleta 
O processo de mineração para o modelo agregou informações plurais para suprir a base:
- **Fontes Estruturadas:** *Endpoints* SPARQL da Wikidata foram requeridos automatizadamente via scripts para mapear e formatar nomes científicos (e.g. *Hydrochoerus hydrochaeris*) e o respectivo status global IUCN das espécies que perpassam as vias. De modo análogo, consumiu-se a API aberta do IBGE para absorver a estratificação geográfica dos limites municipais.
- **Fontes Não Estruturadas:** Foi promovido o escaneamento ativo (via *Web Scraping* usando a biblioteca `BeautifulSoup`) em enciclopédias (*Wikipedia*), *journals* acadêmicos publicamente indexados e em colunas de noticiários ambientais, retirando-se as margens semânticas e o texto em *corpus* puro para posterior inspeção lógica.

## Extratores Baseados em Processamento de Linguagem Natural (NLP)
O núcleo do extrator em Python emprega o pacote linguístico `spaCy` (com o modelo em português `pt_core_news_sm`). O algoritmo opera duplamente para injetar formalismo:
1. Aplica o *Entity Ruler* com dicionários prévios e casamentos REGEX focados no contexto em questão (siglas, biomas do Taim e logradouros como "BR-471"). 
2. Realiza o mapeamento relacional (Triplas S-V-O) percorrendo a árvore sintática da frase e isolando os lemmas dos verbos (*roots*). Sujeitos transitivos e complementos são filtrados para originar triplas (ex: animal `viveEm` banhado, veado `cruzar` rodovia), acionando o mapa predefinido que refina as relações aos predicados suportados da Ontologia.

## Exemplificando Instanciações da Ontologia
Com as triplas filtradas, o *script* `povoa_ontologia.py` atua via bibliotecas de carregamento relacional provendo instâncias autênticas e simuladas com cardinalidade estatística aceitável. Exemplo prático de instanciação da geração OWL final:

```python
# Instanciando a vítima biológica com os seus predicados base e referências taxonômicas 
animal_idx = onto.Mamifero("Mamifero_Sintetico_12")
animal_idx.nomeComum.append("Capivara")
animal_idx.possuiHabitat.append(onto.TipoVegetacao("Banhado_Sintetico_2"))
animal_idx.pertenceAEspecie.append(onto.EspecieAnimal("Especie_Comum_LC_1"))

# Construção material do sinistro no grafo interligando as entidades do domínio ambiental e logístico 
evento = onto.EventoAtropelamento("Evento_Atropelamento_Sintetico_38")
evento.envolveAnimal.append(animal_idx)
evento.ocorreEmRodovia = onto.Rodovia("br_471")
evento.dataEvento.append("2023-08-15")
evento.horaEvento.append("19:00")
evento.condicaoAnimalPosEvento.append("Morto")
```

**Limitações do Acervo Resultante:** Processamentos rasos sob NLP baseados puramente no lema das formas nominais arriscam o carregamento de alucinações nas correferências semânticas (e.g. correlacionar erradamente a localização de um anfíbio distante pelo contexto gramatical vago de uma reportagem jornalística truncada).

# 4. Consultas SPARQL (Destaques)
Conforme requisitos pragmáticos preestabelecidos, o conjunto englobando o total de 30 consultas semânticas exigidas foi integralmente codificado em sintaxe nativa, validado lógicamente sob o viés da consistência estrutural e se encontra disponibilizado de maneira integral nos scripts submetidos (`consultas_sparql_complexo.py`).
Abaixo, encontram-se sumarizadas as 5 mais expressivas e abrangentes consultas que exercitam os múltiplos braços da matriz de conhecimento projetada:

### 4.1 Consulta Simples: Avaliação Operacional de Trechos 
**Descrição:** Transita trivialmente pela listagem das frações e partições da rodovia para extrair variáveis restritas de engenharia de tráfego, garantindo auditoria logística primária.
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX taim: <http://www.semanticweb.org/ontologias/banhado-do-taim/atropelamento-fauna.owl#>

SELECT ?trecho ?kmInicio ?kmFim ?velMax ?largura ?volume
WHERE {
  ?trecho rdf:type taim:TrechoRodoviario .
  ?trecho taim:quilometragemInicial ?kmInicio .
  ?trecho taim:quilometragemFinal ?kmFim .
  ?trecho taim:velocidadeMaximaPermitida ?velMax .
  ?trecho taim:larguraPista ?largura .
  ?trecho taim:volumeMedioTrafego ?volume .
}
ORDER BY ?kmInicio
```
**Amostra dos Resultados Obtidos:** O motor inferencial lista indivíduos (e.g., `Trecho_Sintetico_2`), demarca a quilometragem associada (4.5 ao 9.0), além da velocidade fixada da via (`80.0` km/h) e sua métrica de estreitamento em metros (`8.0`).

### 4.2 Múltiplas Relações (Deep Query): Cadeia Rastreável de Proveniência Ecológica
**Descrição:** Essa consulta perfaz uma varredura cruzada massiva ao longo de 6 níveis lógicos contíguos: o Evento central, o Espécime acometido, sua identificação Binomial Internacional, o Bioma/Habitat, o exato Trecho interceptador e finalmente as Coordenadas Cartesianas absolutas. 
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX taim: <http://www.semanticweb.org/ontologias/banhado-do-taim/atropelamento-fauna.owl#>

SELECT ?evento ?nomeAnimal ?nomeCientifico ?habitat ?trecho ?lat ?lon
WHERE {
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
}
ORDER BY ?evento
```
**Amostra dos Resultados Obtidos:** Garante visão inquebrável, relacionando de forma planar eventos com animais isolados (*Graxaim* / *Cerdocyon thous*), seu nicho natural e a métrica estrita da latitude `-32.55` e longitude `-52.00` interceptada pelo `Trecho 12`.

### 4.3 Consulta com Filtros de Condição Externa: Horário versus Higrometria 
**Descrição:** Identifica a sinergia catastrófica entre janelas temporais de invisibilidade (noturno estendido compreendendo antes das 06:00h ou após as 18:00h) concomitante ao grau acentuado de umidade atmosférica (acima da marca de 80%). Essencialmente detecta surtos mortais incidentes na migração instintiva de Anfíbios.
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX taim: <http://www.semanticweb.org/ontologias/banhado-do-taim/atropelamento-fauna.owl#>

SELECT ?evento ?hora ?umidade ?nomeAnimal
WHERE {
  ?evento rdf:type taim:EventoAtropelamento .
  ?evento taim:horaEvento ?hora .
  ?evento taim:envolveAnimal ?animal .
  ?animal taim:nomeComum ?nomeAnimal .
  ?evento taim:temCondicaoAmbiental ?cond .
  ?cond rdf:type taim:CondicaoClimatica .
  ?cond taim:umidadeRelativa ?umidade .
  FILTER (?umidade > 80.0)
  FILTER (?hora >= "18:00" || ?hora < "06:00")
}
ORDER BY DESC(?umidade)
```
**Amostra dos Resultados Obtidos:** Listagem contendo apenas horários de pico noturno (`22:00`), com umidade relativa retornando valores como `91.0` associada estritamente aos organismos colididos sob referidas intempéries.

### 4.4 Consulta de Agregação Matemática: Cálculo de "Hotspots" de Atropelamentos
**Descrição:** Agrupa programaticamente o conglomerado de incidentes indexando-os pelo próprio nó de seu trecho geográfico percorrido (`GROUP BY`). Destaca, através da ordenação decrescente de seu `COUNT`, os epicentros com mortalidade viária aberrante. 
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX taim: <http://www.semanticweb.org/ontologias/banhado-do-taim/atropelamento-fauna.owl#>

SELECT ?trecho ?kmInicio ?kmFim (COUNT(?evento) AS ?totalEventos)
WHERE {
  ?evento rdf:type taim:EventoAtropelamento .
  ?evento taim:ocorreEmTrecho ?trecho .
  ?trecho taim:quilometragemInicial ?kmInicio .
  ?trecho taim:quilometragemFinal ?kmFim .
}
GROUP BY ?trecho ?kmInicio ?kmFim
ORDER BY DESC(?totalEventos)
```
**Amostra dos Resultados Obtidos:** Devolve a distribuição sumária e agregada de ocorrências, comprovando que, por exemplo, o segmento do km 18 ao 22 englobou 27 dos incidentes apurados, seguido por pontos de incidência média e nula.

### 4.5 Cenário de Domínio Avaliativo: Indicação Fática de Passagem de Fauna 
**Descrição:** Modelagem de cruzamento vital para tomada de decisão no ambiente do Taim. Avalia de forma cruzada onde (a) espécimes colidiram fatalmente no asfalto e, de modo agravante (b) constata-se pela topologia que a rodovia interceptou o núcleo de vivência silvestre deste mesmo espécime morto. Revela sem margens à dúvida os trechos para escavação urgente de túneis ecodutos direcionados. 
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX taim: <http://www.semanticweb.org/ontologias/banhado-do-taim/atropelamento-fauna.owl#>

SELECT DISTINCT ?trecho ?kmInicio ?kmFim ?nomeAnimal ?habitatComum ?velMax
WHERE {
  ?evento rdf:type taim:EventoAtropelamento .
  ?evento taim:envolveAnimal ?animal .
  ?animal taim:nomeComum ?nomeAnimal .
  ?animal taim:possuiHabitat ?habitatComum .
  ?evento taim:ocorreEmTrecho ?trecho .
  ?trecho taim:atravessaHabitat ?habitatComum .
  ?trecho taim:quilometragemInicial ?kmInicio .
  ?trecho taim:quilometragemFinal ?kmFim .
  ?trecho taim:velocidadeMaximaPermitida ?velMax .
}
ORDER BY ?kmInicio
```
**Amostra dos Resultados Obtidos:** Fatos depurados mostrando segmentação crítica, onde a presença biológica cruza-se transversalmente e sem alternativa com infraestrutura asfáltica.

*(Nota Documental: Tendo em vista a ausência de injeção de parâmetros computacionais explícitos ou de pacotes pré-treinados em Machine Learning nas entregas originais apuradas, a seção estrita abordando a explicabilidade de arquitetura preditiva via IA Simbólica não se julga condizente com o subproduto atual do projeto, restando preterida nesta elaboração).*

# 5. Conclusão

O ecossistema estrutural originado da confecção da ontologia cumpre com integridade a meta pragmática de agrupar sob uma fundação lógica semântica os metadados fluídos referentes ao bioma do Banhado do Taim. O escalonamento da taxonomia se evidenciou plenamente apto a entrelaçar e isolar os vértices antropogênicos da pista da infraestrutura e as métricas do nicho faunístico. A engrenagem de povoamento guiada por métodos reativos, englobando capturas em APIs oficiais da administração, extrações do Wikidata e refinamentos léxicos via NLP de material informal, sustenta e corrobora positivamente o potencial técnico e o uso versátil da inteligência artificial retroativa nos grafos. 

As expansões deste projeto apontam para um intercâmbio contínuo e orgânico. Com acesso futuro ao fluxo interativo de dados (*streamings* reais de medidores sensoriais da rodovia e de microclima), o maquinário OWL poderá ser elevado da função exclusiva de catalogação passiva ao patamar prescritivo – alertando precocemente equipes em tempo real sobre instabilidades nas variáveis climáticas em trechos adjacentes a biomas suscetíveis a migração pontual. A transposição primária deste viés puramente sintático e empírico, se atrelada a agentes autônomos curadores, representará um passo indelével em vias de erradicação sistêmica na fatalidade destas intersecções ambientais críticas.
