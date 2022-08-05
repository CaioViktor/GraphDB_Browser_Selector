from flask import Flask,render_template,request, redirect, url_for
from SPARQLWrapper import SPARQLWrapper, JSON
from saved_queries import saved_queries
import hashlib
import json
import urllib.parse

# ENDPOINT_ONTOLOGY = "http://localhost:7200/repositories/onto"
# ENDPOINT_RESOURCES = "http://localhost:7200/repositories/virtual"
# GRAPHDB_BROWSER = "http://localhost:7200/graphs-visualizations"
# GRAPHDB_BROWSER_CONFIG = "1b4a405cc5c4431dab894b1ee3e73fb9"

# ENDPOINT_ONTOLOGY = "http://10.33.96.18:7200/repositories/ONTOLOGIA_DOMINIO"
# ENDPOINT_RESOURCES = "http://10.33.96.18:7200/repositories/GRAFO_SEFAZMA"
# GRAPHDB_BROWSER = "http://10.33.96.18:7200/graphs-visualizations"
# GRAPHDB_BROWSER_CONFIG = "4fc22232f35e44878c819ee03543e852"


# ENDPOINT_ONTOLOGY = "http://10.33.96.18:7200/repositories/ONTOLOGIA_ENDERECO"
# ENDPOINT_RESOURCES = "http://10.33.96.18:7200/repositories/GRAFO_ENDERECO"
# GRAPHDB_BROWSER = "http://10.33.96.18:7200/graphs-visualizations"
# GRAPHDB_BROWSER_CONFIG = "4fc22232f35e44878c819ee03543e852"

# ENDPOINT_ONTOLOGY = "http://10.33.96.18:7200/repositories/ONTOLOGIA_DOMINIO"
# ENDPOINT_RESOURCES = "http://10.33.96.18:7200/repositories/GRAFO_SEFAZMA_TESTES"
# GRAPHDB_BROWSER = "http://10.33.96.18:7200/graphs-visualizations"
# GRAPHDB_BROWSER_CONFIG = "4fc22232f35e44878c819ee03543e852"


ENDPOINT_ONTOLOGY = "http://10.33.96.18:7200/repositories/ONTOLOGIA_DOMINIO"
ENDPOINT_RESOURCES = "http://10.33.96.18:7200/repositories/GRAFO_SEFAZMA_PRODUCAO"
GRAPHDB_BROWSER = "http://10.33.96.18:7200/graphs-visualizations"
GRAPHDB_BROWSER_CONFIG = "4fc22232f35e44878c819ee03543e852"
ENDPOINT_HISTORY = "http://localhost:7200/repositories/Hist"

sparql_ontology = SPARQLWrapper(ENDPOINT_ONTOLOGY)
sparql_resources = SPARQLWrapper(ENDPOINT_RESOURCES)
sparql_history = SPARQLWrapper(ENDPOINT_HISTORY)

# return redirect(url_for('controle_consistencias',mensagem=mensagem))

app = Flask(__name__)

@app.route("/")
def index():    
    return render_template("index.html")

@app.route("/resources/<page>/")
def resources(page,methods=['GET']):
    search = request.args.get('search',default="")
    classRDF = request.args.get('classRDF',default="")
    label = request.args.get('label',default="Busca")
    return render_template("resources.html",page=page,search=search,classRDF=classRDF,label=label)


@app.route("/classes")
def classes():
    query = """
        prefix owl: <http://www.w3.org/2002/07/owl#>
        prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        select ?class ?label where { 
            {
                ?class a owl:Class.
            }
            UNION{
                ?class a rdfs:Class.
            }
            OPTIONAL{?class rdfs:label ?l}
            BIND(COALESCE(?l,?class) AS ?label)
            FILTER(!CONTAINS(STR(?class),"http://www.w3.org/2000/01/rdf-schema#"))
            FILTER(!CONTAINS(STR(?class),"http://www.w3.org/2001/XMLSchema#"))
            FILTER(!CONTAINS(STR(?class),"http://www.w3.org/1999/02/22-rdf-syntax-ns#"))
            FILTER(!CONTAINS(STR(?class),"http://www.w3.org/2002/07/owl#"))
        } ORDER BY ?label       
    """
    sparql_ontology.setQuery(query)
    # print(query)
    sparql_ontology.setReturnFormat(JSON)
    results = sparql_ontology.query().convert()
    properties = {}
    classes = []
    for result in results["results"]["bindings"]:
        class_ = {'uri':urllib.parse.quote(result['class']['value']),'label':result['label']['value']}
        if "/" in class_['label']:
            class_['label'] = class_['label'].split("/")[-1].split("#")[-1]
        classes.append(class_)
    return json.dumps(classes, ensure_ascii=False).encode('utf8')


@app.route("/list_resources/<page>")
def list_resources(page,methods=['GET']):
    offset = int(page) * 100
    search = request.args.get('search',default="")
    classRDF = request.args.get('classRDF',default="")

    filterSearch = ""
    if search != None and search != '':
        filterSearch = f"""FILTER(REGEX(STR(?resource),"{search}","i") || REGEX(STR(?label),"{search}","i"))"""
    if classRDF != None and classRDF != '':
        query = f"""
            prefix owl: <http://www.w3.org/2002/07/owl#>
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            select ?resource ?label where {{ 
                ?resource a <{classRDF}>.
                ?resource rdfs:label ?l
                BIND(COALESCE(?l,?resource) AS ?label)
                {filterSearch}
            }}
            LIMIT 100
            OFFSET {offset}
        """
    else:
        query = f"""
            prefix owl: <http://www.w3.org/2002/07/owl#>
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            select ?resource ?label where {{ 
                ?resource ?p _:x2.
                ?resource rdfs:label ?l
                BIND(COALESCE(?l,?resource) AS ?label)
                {filterSearch}
            }}
            LIMIT 100
            OFFSET {offset}
        """
    sparql_resources.setQuery(query)
    # print(query)
    sparql_resources.setReturnFormat(JSON)
    results = sparql_resources.query().convert()
    resources = []
    for result in results["results"]["bindings"]:
        resource = {'uri':urllib.parse.quote(result['resource']['value']),'label':result['label']['value'],'graphdb_url':GRAPHDB_BROWSER+"?config="+GRAPHDB_BROWSER_CONFIG+"&uri="+urllib.parse.quote(result['resource']['value'])+"&embedded"}
        if "/" in resource['label']:
            resource['label'] = resource['label'].split("/")[-1].split("#")[-1]
        resources.append(resource)
    return json.dumps(resources, ensure_ascii=False).encode('utf8')



# @app.route("/list_atributos_hist/")
# def list_atributos_hist():
#     uri = request.args.get('uri',default="")#http://www.sefaz.ma.gov.br/ontology/Estabelecimento
#     if uri != 'null':
#         query = f"""
#             prefix owl: <http://www.w3.org/2002/07/owl#>
#             prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#             prefix tl: <http://purl.org/NET/c4dm/timeline.owl#>
#             prefix sfz: <http://www.sefaz.ma.gov.br/ontology/>
#             PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
#             SELECT DISTINCT ?campo WHERE{{
#                 ?estabelecimento a <{uri}>;
#                     sfz:tem_timeLine ?tl.
#                 ?inst tl:timeLine ?tl;
#                     sfz:tem_atualizacao ?att.
#                 ?att sfz:atributo ?campo.       
#             }}
#             ORDER BY ?campo
#         """
    
#     sparql_history.setQuery(query)
#     # print(query)
#     sparql_history.setReturnFormat(JSON)
#     results = sparql_history.query().convert()
#     resources = []
#     for result in results["results"]["bindings"]:
#         resource = result['campo']['value']
#         resources.append(resource)
#     return json.dumps(resources, ensure_ascii=False).encode('utf8')

# @app.route("/get_propriedade")
# def get_propriedade():
#     recurso = request.args.get('recurso',default=None)
#     atributo = request.args.get('atributo',default=None)
#     data = request.args.get('data',default=None)
    
#     query = f"""
#         prefix owl: <http://www.w3.org/2002/07/owl#>
#         prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#         prefix tl: <http://purl.org/NET/c4dm/timeline.owl#>
#         prefix sfz: <http://www.sefaz.ma.gov.br/ontology/>
#         PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
#         SELECT ?data ?n_serie ?campo ?campo_r  ?va ?vn WHERE{{
#             <{recurso}> sfz:tem_timeLine ?tl.
#             ?inst tl:timeLine ?tl;
#                 sfz:tem_atualizacao ?att;
#                 tl:atDate ?data.
#             ?att sfz:valor_antigo ?va;
#                 sfz:valor_novo ?vn;
#                 sfz:atributo ?campo;
#                 sfz:atributo_relacional ?campo_r;
#                 sfz:numero_serie ?n_serie.
#             FILTER(CONTAINS("{atributo}",?campo))
#             FILTER(?data <= "{data}"^^xsd:dateTime) 
#         }}
#         ORDER BY DESC(?n_serie) DESC(?data) 
#         LIMIT 1
#     """.format(recurso,atributo,data)
    
#     sparql_history.setQuery(query)
#     # print(query)
#     sparql_history.setReturnFormat(JSON)
#     results = sparql_history.query().convert()
#     resources = []
#     for result in results["results"]["bindings"]:
#         resource = result['campo']['value']
#         resources.append(resource)
#     return json.dumps(resources, ensure_ascii=False).encode('utf8')

@app.route("/list_saved")
def list_saved():
    return render_template("list_saved.html",saved_queries=saved_queries)



@app.route("/list_itens_saved/<id>/<page>")
def list_itens_saved(id,page):
    return render_template("list_itens_saved.html",id=id,page=page)


@app.route("/query_saved/<id>/<page>")
def query_saved(id,page):
    offset = int(page) * 100
    id = int(id)
    item = saved_queries[id]
    query = item['query'] + f"\nOFFSET {offset}"
    sparql_resources.setQuery(query)
    # print(query)
    sparql_resources.setReturnFormat(JSON)
    results = sparql_resources.query().convert()
    resources = []
    for result in results["results"]["bindings"]:
        query_construct = item['construct_query'].replace("$URI",result[item['uri_var']]['value']) 
        resource = {'graphdb_url':GRAPHDB_BROWSER+"?config="+GRAPHDB_BROWSER_CONFIG+"&query="+urllib.parse.quote(query_construct)+"&embedded"}
        for var in result:
            resource[var] = result[var]['value']
        resources.append(resource)
    return json.dumps({'vars':results['head']['vars'],'resources':resources}, ensure_ascii=False).encode('utf8')

# @app.route("/atributo_data")
# def atributo_data():
#     classe = request.args.get('classe',default=None)
#     atributo = request.args.get('atributo',default=None)
#     data = request.args.get('data',default=None)
#     return render_template("atributo_data.html",classe=classe,atributo=atributo,data=data)


@app.route("/get_historico")
def get_historico():
    uri = request.args.get('uri',default=None)
    query = """
    prefix owl: <http://www.w3.org/2002/07/owl#>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix tl: <http://purl.org/NET/c4dm/timeline.owl#>
    prefix sfz: <http://www.sefaz.ma.gov.br/ontology/>
    SELECT ?data ?n_serie ?campo  ?va ?vn WHERE {
    <$uri> sfz:tem_timeLine ?tl.
        ?inst tl:timeLine ?tl;
        sfz:tem_atualizacao ?att;
        tl:atDate ?data.
    ?att sfz:valor_antigo ?va;
        sfz:valor_novo ?vn;
        sfz:atributo ?campo;
        sfz:atributo_relacional ?campo_r;            
        sfz:numero_serie ?n_serie.
    }
    ORDER BY ?data ?n_serie ?campo 
    """.replace("$uri",uri)
    
    sparql_history.setQuery(query)
    # print(query)
    sparql_history.setReturnFormat(JSON)
    results = sparql_history.query().convert()
    resources_historico_data = {}
    for result in results["results"]["bindings"]:
        data = result['data']['value']
        if not data in resources_historico_data:
            resources_historico_data[data]= {}
        if not result['campo']['value'] in resources_historico_data[data]:
            resources_historico_data[data][result['campo']['value']] = []
        resources_historico_data[data][result['campo']['value']].append({'valor_antigo': result['va']['value'],'valor_novo': result['vn']['value']})
    

    resources_historico_propriedade = {}
    for result in results["results"]["bindings"]:
        data = result['data']['value']
        propriedade = result['campo']['value']
        if not propriedade in resources_historico_propriedade:
            resources_historico_propriedade[propriedade]= {}
        if not data in resources_historico_propriedade[propriedade]:
            resources_historico_propriedade[propriedade][data] = []
        resources_historico_propriedade[propriedade][data].append({'valor_antigo': result['va']['value'],'valor_novo': result['vn']['value']})
    
    # query = """
    
    # SELECT ?p ?o WHERE {
    #     <$uri> ?p ?o
    # }
    # """.replace("$uri",uri)
    
    # sparql_history.setQuery(query)
    # # print(query)
    # sparql_resources.setReturnFormat(JSON)
    # results = sparql_resources.query().convert()
    # resources_atual = {}
    # for result in results["results"]["bindings"]:
    #     data = result['data']['value']
    #     if not data in resources_historico:
    #         resources_historico[data]= []
    #     att = {
    #         result['campo']['value']:{
    #             'valor_antigo': result['va']['value'],
    #             'valor_novo': result['vn']['value']
    #         }
    #     }
    #     resources_historico[data].append(att)
    resources = {'resources_historico_propriedade':resources_historico_propriedade,'resources_historico_data':resources_historico_data}
    return json.dumps(resources, ensure_ascii=False).encode('utf8')


@app.route("/historico_recurso")
def historico_recurso():
    uri = request.args.get('uri',default=None)
    
    return render_template("historico_recurso.html",uri=uri)

if __name__ == "__main__":
    # app.run(host='10.33.96.18',port=1111) #Colocar IP da máquina hospedeira (Servidor) aqui
    app.run(host='0.0.0.0',port=1111)