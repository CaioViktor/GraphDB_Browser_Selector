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

ENDPOINT_ONTOLOGY = "http://10.33.96.18:7200/repositories/ONTOLOGIA_DOMINIO"
ENDPOINT_RESOURCES = "http://10.33.96.18:7200/repositories/GRAFO_SEFAZMA"
GRAPHDB_BROWSER = "http://10.33.96.18:7200/graphs-visualizations"
GRAPHDB_BROWSER_CONFIG = "4fc22232f35e44878c819ee03543e852"


# ENDPOINT_ONTOLOGY = "http://10.33.96.18:7200/repositories/ONTOLOGIA_ENDERECO"
# ENDPOINT_RESOURCES = "http://10.33.96.18:7200/repositories/GRAFO_ENDERECO"
# GRAPHDB_BROWSER = "http://10.33.96.18:7200/graphs-visualizations"
# GRAPHDB_BROWSER_CONFIG = "4fc22232f35e44878c819ee03543e852"

sparql_ontology = SPARQLWrapper(ENDPOINT_ONTOLOGY)
sparql_resources = SPARQLWrapper(ENDPOINT_RESOURCES)

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
        filterSearch = f"""FILTER(CONTAINS(STR(?resource),"{search}") || CONTAINS(STR(?label),"{search}"))"""
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
        resource = {'uri':urllib.parse.quote(result['resource']['value']),'label':result['label']['value'],'graphdb_url':GRAPHDB_BROWSER+"?config="+GRAPHDB_BROWSER_CONFIG+"&uri="+urllib.parse.quote(result['resource']['value'])}
        if "/" in resource['label']:
            resource['label'] = resource['label'].split("/")[-1].split("#")[-1]
        resources.append(resource)
    return json.dumps(resources, ensure_ascii=False).encode('utf8')

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
        query_construct = item['construct_query'].replace("$URI",result['estabelecimento_rfb']['value']) 
        resource = {'label':result['nome_fantasia_rfb']['value'],'graphdb_url':GRAPHDB_BROWSER+"?config="+GRAPHDB_BROWSER_CONFIG+"&query="+urllib.parse.quote(query_construct)}
        resources.append(resource)
    return json.dumps(resources, ensure_ascii=False).encode('utf8')

if __name__ == "__main__":
    app.run(host='10.33.96.18',port=1111) #Colocar IP da máquina hospedeira (Servidor) aqui
    # app.run(host='0.0.0.0',port=1111)