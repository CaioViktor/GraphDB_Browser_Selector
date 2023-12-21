# LIght Rdf Browser (LiRB) 
# Repository configuration file
#
#
#

#Default configuration
#
# ENDPOINT_ONTOLOGY = "http://localhost:7200/repositories/YOUR"#Endpoint for ontology
# ENDPOINT_RESOURCES = "http://localhost:7200/repositories/YOUR"#Endpoint for resources
# ENDPOINT_HISTORY = "http://localhost:7200/repositories/YOUR"#Endpoint for history
# GRAPHDB_BROWSER = "http://localhost:7200/graphs-visualizations"#URL for browser graph-visualization
# GRAPHDB_BROWSER_CONFIG = '' #set '' if uses default graph-visualization, '&config=ID' for custom graph-visualization config
# USE_N_ARY_RELATIONS = True #Read n-ary relations as metadata
# USE_LABELS = True #Set True to get labels for resources. When querying virtual repositories maybe be better set to False
# HIGHLIGHT_CLASSES = [] #A list with URIs of highlighted classes
#

#LOCAL
# ENDPOINT_ONTOLOGY = "http://localhost:7200/repositories/artigo"
# ENDPOINT_RESOURCES = "http://localhost:7200/repositories/artigo"
# ENDPOINT_HISTORY = "http://localhost:7200/repositories/artigo"
# GRAPHDB_BROWSER = "http://localhost:7200/graphs-visualizations"
# GRAPHDB_BROWSER_CONFIG = ""
# USE_N_ARY_RELATIONS = True
# USE_LABELS = True 
# HIGHLIGHT_CLASSES = ['http://www.example.lirb.com/Person','http://www.example.lirb.com/Company']


# SEFAZ-MA CONTEXTO
# ENDPOINT_ONTOLOGY = "http://localhost:7200/repositories/ONTOLOGIA_DOMINIO"
# ENDPOINT_RESOURCES = "http://localhost:7200/repositories/GRAFO_PRODUCAO_MATERIALIZADO"
# ENDPOINT_HISTORY = "http://localhost:7200/repositories/GRAFO_PRODUCAO_MATERIALIZADO"
# GRAPHDB_BROWSER = "http://localhost:7200/graphs-visualizations"
# HIGHLIGHT_CLASSES = ['http://xmlns.com/foaf/0.1/Organization','http://www.sefaz.ma.gov.br/ontology/Estabelecimento', 'http://xmlns.com/foaf/0.1/Person', 'http://www.sefaz.ma.gov.br/ontology/Sociedade'] #A list with URIs of highlighted classes
# MAIN_DATA_SOURCE = "Cadastro_SEFAZ-MA"
# GRAPHDB_BROWSER_CONFIG = "&config=63b76b9865064cd8a9775e1e2f46ff4d"
# USE_N_ARY_RELATIONS = False
# USE_LABELS = True #Set True to get labels for resources. When querying virtual repositories maybe be better set to False

# SEMANTIC-FORTALEZA
ENDPOINT_ONTOLOGY = "http://localhost:7200/repositories/ONTOLOGIA_DOMINIO_BIGSEMFORTALEZA"
ENDPOINT_RESOURCES = "http://localhost:7200/repositories/GRAFO_PRODUCAO_BIGSEMFORTALEZA"
GRAPHDB_BROWSER = "http://localhost:7200/graphs-visualizations"
GRAPHDB_BROWSER_CONFIG = "&config=63b76b9865064cd8a9775e1e2f46ff4d"
ENDPOINT_HISTORY = "http://localhost:7200/repositories/GRAFO_PRODUCAO_BIGSEMFORTALEZA"
USE_N_ARY_RELATIONS = False
USE_LABELS = True #Set True to get labels for resources. When querying virtual repositories maybe be better set to False
HIGHLIGHT_CLASSES = ['http://xmlns.com/foaf/0.1/Organization','http://www.sefaz.ma.gov.br/ontology/Estabelecimento', 'http://xmlns.com/foaf/0.1/Person', 'http://www.sefaz.ma.gov.br/ontology/Sociedade'] #A list with URIs of highlighted classes
MAIN_DATA_SOURCE = "criancasMatriculadas"
