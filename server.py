from flask import Flask,render_template,request, redirect, url_for
from SPARQLWrapper import SPARQLWrapper, JSON
from saved_queries import saved_queries
from flask import jsonify
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

sparql_ontology = SPARQLWrapper(ENDPOINT_ONTOLOGY)
sparql_resources = SPARQLWrapper(ENDPOINT_RESOURCES)

list_classes_destaque = ['http://www.sefaz.ma.gov.br/ontology/Contribuinte','http://xmlns.com/foaf/0.1/Organization','http://www.sefaz.ma.gov.br/ontology/Endereco','http://www.sefaz.ma.gov.br/ontology/Estabelecimento','http://www.sefaz.ma.gov.br/ontology/Fornecedor','http://xmlns.com/foaf/0.1/Person','http://www.sefaz.ma.gov.br/ontology/Socio',]

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
        select ?class ?label (GROUP_CONCAT(?c;separator=".\\n") as ?comment) where { 
            {
                ?class a owl:Class.
            }
            UNION{
                ?class a rdfs:Class.
            }
            OPTIONAL{?class rdfs:label ?l}
    		OPTIONAL{?class rdfs:comment ?c}
            BIND(COALESCE(?l,?class) AS ?label)
            FILTER(!CONTAINS(STR(?class),"http://www.w3.org/2000/01/rdf-schema#"))
            FILTER(!CONTAINS(STR(?class),"http://www.w3.org/2001/XMLSchema#"))
            FILTER(!CONTAINS(STR(?class),"http://www.w3.org/1999/02/22-rdf-syntax-ns#"))
            FILTER(!CONTAINS(STR(?class),"http://www.w3.org/2002/07/owl#"))
        }GROUP BY ?class ?label
        ORDER BY ?label  
		     
    """
    sparql_ontology.setQuery(query)
    # print(query)
    sparql_ontology.setReturnFormat(JSON)
    results = sparql_ontology.query().convert()
    classes = []
    classes_destaque = []
    for result in results["results"]["bindings"]:
            
        class_ = {'uri':urllib.parse.quote(result['class']['value']),'uri_raw':result['class']['value'],'label':result['label']['value'],'comment':result['comment']['value']}
        if "/" in class_['label']:
            class_['label'] = class_['label'].split("/")[-1].split("#")[-1]
        classes.append(class_)
        if result['class']['value'] in list_classes_destaque:
            classes_destaque.append(class_)
    return json.dumps({'classes':classes,'classes_destaque':classes_destaque}, ensure_ascii=False).encode('utf8')

@app.route("/propriedades")
def propriedades():
    query = """
        prefix owl: <http://www.w3.org/2002/07/owl#>
        prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        select ?property ?label where { 
            {
                ?property a owl:ObjectProperty.
            }
    		UNION{
                ?property a owl:DatatypeProperty.
            }
            UNION{
                ?property a rdfs:Property.
            }
            OPTIONAL{?property rdfs:label ?l}
            BIND(COALESCE(?l,?property) AS ?label)
        }
        ORDER BY ?label  
    """
    sparql_ontology.setQuery(query)
    # print(query)
    sparql_ontology.setReturnFormat(JSON)
    results = sparql_ontology.query().convert()
    propriedades = {}
    for result in results["results"]["bindings"]:
            
        label = result['label']['value']
        if "/" in label:
            label = label.split("/")[-1].split("#")[-1]
        propriedades[result['property']['value']] = label

    return json.dumps({'propriedades':propriedades}, ensure_ascii=False).encode('utf8')


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
        if "http://" in resource['label'] or "https://" in resource['label']:
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
        query_construct = item['construct_query'].replace("$URI",result[item['uri_var']]['value']) 
        resource = {'graphdb_url':GRAPHDB_BROWSER+"?config="+GRAPHDB_BROWSER_CONFIG+"&query="+urllib.parse.quote(query_construct)+"&embedded"}
        for var in result:
            resource[var] = result[var]['value']
        resources.append(resource)
    return json.dumps({'vars':results['head']['vars'],'resources':resources}, ensure_ascii=False).encode('utf8')


@app.route("/browser")
def browser(methods=['GET']):
    uri = request.args.get('uri',default="")
    return render_template("browser.html",uri=uri)

@app.route("/get_properties")
def get_properties(methods=['GET']):
    uri = request.args.get('uri',default="")
    query = f"""
        SELECT ?p ?o WHERE{{
            <{uri}> ?p ?o.    
        }} ORDER BY ?p		     
    """
    sparql_resources.setQuery(query)
    # print(query)
    sparql_resources.setReturnFormat(JSON)
    results = sparql_resources.query().convert()
    properties = {}
    
    for result in results["results"]["bindings"]:
        if not result['p']['value'] in properties:
            properties[result['p']['value']] = []
        properties[result['p']['value']].append(result['o']['value'])
    propriedades_list = json.loads(propriedades())['propriedades']
    classes_list = {}
    for classe in json.loads(classes())['classes']:
        classes_list[classe['uri_raw']] = classe['label']
    
    return jsonify({'properties':properties,'propriedades_list':propriedades_list,'classes_list':classes_list,'graphdb_link':GRAPHDB_BROWSER+"?config="+GRAPHDB_BROWSER_CONFIG+"&uri="+urllib.parse.quote(uri)+"&embedded"})
if __name__ == "__main__":
    # app.run(host='10.33.96.18',port=1111) #Colocar IP da máquina hospedeira (Servidor) aqui
    app.run(host='0.0.0.0',port=1111)