from flask import Flask,render_template,request, redirect, url_for
from SPARQLWrapper import SPARQLWrapper, JSON
from saved_queries import saved_queries
from flask import jsonify
import json
import urllib.parse
from config import *




sparql_ontology = SPARQLWrapper(ENDPOINT_ONTOLOGY)
sparql_resources = SPARQLWrapper(ENDPOINT_RESOURCES)
sparql_history = SPARQLWrapper(ENDPOINT_HISTORY)


list_highlights_classes = []
query = """
    prefix owl: <http://www.w3.org/2002/07/owl#>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix optq: <http://eu.optique.ontology/annotations#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    select ?class where {
        ?class optq:tem_destaque "true"^^xsd:boolean
    }
"""
sparql_ontology.setQuery(query)
# print(query)
sparql_ontology.setReturnFormat(JSON)
results = sparql_ontology.query().convert()
for result in results["results"]["bindings"]:
    list_highlights_classes.append(result['class']['value'])

# if len(list_highlights_classes) == 0:
list_highlights_classes = HIGHLIGHT_CLASSES

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
		select ?class ?label (MAX(?c) as ?comment) where { 
            {
                ?class a owl:Class.
            }
            UNION{
                ?class a rdfs:Class.
            }
            OPTIONAL{
                ?class rdfs:label ?l.
        		FILTER(lang(?l)="pt")
            
            }
    		OPTIONAL{
                ?class rdfs:comment ?c1.
        		FILTER(lang(?c1)="pt")
            }
            BIND(COALESCE(?l,?class) AS ?label)
    		BIND(COALESCE(?c1,"") AS ?c)
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
    highlight_classes = []
    for result in results["results"]["bindings"]:
        query = f"""
            prefix owl: <http://www.w3.org/2002/07/owl#>
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            select ?sub ?label where {{ 
                ?sub rdfs:subClassOf <{result['class']['value']}>.
                OPTIONAL{{
                    ?sub rdfs:label ?l.
                
                }}
                BIND(COALESCE(?l,?sub) AS ?label)
            }}
            ORDER BY ?label  
        """
        subclasses = []
        sparql_ontology.setQuery(query)
        # print(query)
        sparql_ontology.setReturnFormat(JSON)
        results_subclass = sparql_ontology.query().convert()
        for result_subclass in results_subclass["results"]["bindings"]:
            uri = result_subclass['sub']['value']
            label = result_subclass['label']['value']
            if 'http' in label:
                label = label.split("/")[-1].split("#")[-1]
            subclasses.append([uri,label])
        class_ = {'uri':urllib.parse.quote(result['class']['value']),'uri_raw':result['class']['value'],'label':result['label']['value'],'comment':result['comment']['value'],'subclasses':subclasses}
        if "http" in class_['label']:
            class_['label'] = class_['label'].split("/")[-1].split("#")[-1]
        classes.append(class_)
        if result['class']['value'] in list_highlights_classes:
            highlight_classes.append(class_)
    return json.dumps({'classes':classes,'highlight_classes':highlight_classes}, ensure_ascii=False).encode('utf8')

@app.route("/properties")
def properties():
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
            OPTIONAL{
                ?property rdfs:label ?l
            
            }
            BIND(COALESCE(?l,?property) AS ?label)
        }
        ORDER BY ?label  
    """
    sparql_ontology.setQuery(query)
    # print(query)
    sparql_ontology.setReturnFormat(JSON)
    results = sparql_ontology.query().convert()
    properties = {}
    for result in results["results"]["bindings"]:
        label = result['label']['value']
        if "http" in label:
            label = label.split("/")[-1].split("#")[-1]
        properties[result['property']['value']] = label
    return json.dumps({'properties':properties}, ensure_ascii=False).encode('utf8')


@app.route("/list_resources/<page>")
def list_resources(page,methods=['GET']):
    offset = int(page) * 100
    search = request.args.get('search',default="")
    classRDF = request.args.get('classRDF',default="")

    label_query = ""
    if USE_LABELS:
        label_query = """{
                    ?resource rdfs:label ?l.
                }"""
    filterSearch = ""
    if search != None and search != '':
        filterSearch = f"""FILTER(REGEX(STR(?resource),"{search}","i") || REGEX(STR(?label),"{search}","i"))"""
    if classRDF != None and classRDF != '':
        query = f"""
            prefix owl: <http://www.w3.org/2002/07/owl#>
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            select ?resource ?label where {{ 
                ?resource a <{classRDF}>.
                OPTIONAL {label_query}
                BIND(COALESCE(?l,?resource) AS ?label)
                {filterSearch}
                FILTER(!CONTAINS(STR(?resource),"http://www.sefaz.ma.gov.br/resource/AppEndereco/"))
                FILTER(!CONTAINS(STR(?resource),"http://www.sefaz.ma.gov.br/resource/AppRazaoSocial/"))
                FILTER(!CONTAINS(STR(?resource),"http://www.sefaz.ma.gov.br/resource/AppNomeFantasia/"))
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
                OPTIONAL {label_query}
                BIND(COALESCE(?l,?resource) AS ?label)
                {filterSearch}
                FILTER(!CONTAINS(STR(?resource),"www.sefaz.ma.gov.br/resource/AppEndereco/"))
                FILTER(!CONTAINS(STR(?resource),"http://www.sefaz.ma.gov.br/resource/AppRazaoSocial/"))
                FILTER(!CONTAINS(STR(?resource),"http://www.sefaz.ma.gov.br/resource/AppNomeFantasia/"))
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
        resource = {'uri':urllib.parse.quote(result['resource']['value']),'label':result['label']['value'],'graphdb_url':GRAPHDB_BROWSER+"?uri="+urllib.parse.quote(result['resource']['value'])+GRAPHDB_BROWSER_CONFIG+"&embedded"}
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
        query_construct = item['construct_query'].replace("$selection_triple",result[item['uri_var']]['value']) 
        # print(query_construct)
        resource = {'graphdb_url':GRAPHDB_BROWSER+"?query="+urllib.parse.quote(query_construct)+GRAPHDB_BROWSER_CONFIG+"&embedded"}
        for var in result:
            resource[var] = result[var]['value']
        resources.append(resource)
    return json.dumps({'vars':results['head']['vars'],'resources':resources}, ensure_ascii=False).encode('utf8')


@app.route("/browser")
def browser(methods=['GET']):
    uri = request.args.get('uri',default="")
    expand_sameas = request.args.get('expand_sameas',default="False")
    if expand_sameas == "True" :
        expand_sameas = True
    else:
        expand_sameas = False
    return render_template("browser.html",uri=uri,USE_LABELS=USE_LABELS,expand_sameas=expand_sameas)

@app.route("/get_properties")
def get_properties(methods=['GET']):
    uri = request.args.get('uri',default="")
    print('<>')
    print('<uri>',uri)

    expand_sameas = request.args.get('expand_sameas',default="False")
    print('<expand_sameas>',expand_sameas)
    if expand_sameas == "True" :
        EXPAND_SAMEAS = True
    else:
        EXPAND_SAMEAS = False

    select = f"""SELECT distinct ?same ?p ?o WHERE {{"""
    selection_triple = f"""{{ 
                <{uri}> ?p ?o. # Quando é a 2ª fonte, não tem owl:sameAs
                bind(<{uri}> as ?same).
            }}
            UNION
            {{
                ?uri owl:sameAs <{uri}>. 
                ?uri owl:sameAs ?sam.
                FILTER(!CONTAINS(STR(?sam),"{uri}")).
                bind(<{uri}> as ?same).
                bind(owl:sameAs as ?p).
                bind(?sam as ?o).
            }}
            UNION
            {{
                ?u owl:sameAs <{uri}>. 
                bind(<{uri}> as ?same).
                bind(owl:sameAs as ?p).
                bind(?u as ?o).
            }}
            """
    if EXPAND_SAMEAS:
        select = f"select ?same ?p ?o where {{"
        if MAIN_DATA_SOURCE in uri:
            selection_triple = f"""
                {{
                    <{uri}> ?p ?o. 
                    bind(<{uri}> as ?same).
                    FILTER(!CONTAINS(STR(?o),"http://www.sefaz.ma.gov.br/resource/App")).
                }}
                UNION {{
                    <{uri}> owl:sameAs ?sam .
                    ?sam ?p ?o.
                    FILTER(!CONTAINS(STR(?sam),"http://www.sefaz.ma.gov.br/resource/App")).
                    FILTER(!CONTAINS(STR(?sam),"{uri}")).
                    bind(?sam as ?same)
                }}
                UNION {{
                    BIND(<{uri}> AS ?same)
                    BIND(owl:sameAs as ?p)
                    BIND(<{uri}> AS ?o)
                }}
            """
        else:
            selection_triple= f"""
                    {{
                        <{uri}> ?p ?o .
                        BIND (<{uri}> AS ?same)
                        # Quando vai para a VU estando na VH
                        FILTER(!CONTAINS(STR(?same),"http://www.sefaz.ma.gov.br/resource/App")).
                    }}
                    UNION {{
                        ?same owl:sameAs <{uri}> .
                        ?same ?p ?o.
                        FILTER(!CONTAINS(STR(?o),"http://www.sefaz.ma.gov.br/resource/App")).
                    }}
                    UNION {{
                        ?uri owl:sameAs <{uri}> .
                        ?uri owl:sameAs ?sam .
                        ?sam ?p ?o.
                        FILTER(!CONTAINS(STR(?sam),"http://www.sefaz.ma.gov.br/resource/App")).
                        FILTER(!CONTAINS(STR(?sam),"{uri}")).
                        bind(?sam as ?same)
                    }}
                    UNION {{
                        ?same owl:sameAs <{uri}> .
                        BIND(owl:sameAs as ?p)
                        BIND(?same AS ?o)
                    }}
                    # FILTER(?p != owl:sameAs)
            """
    if not USE_N_ARY_RELATIONS:
        query = f"""{select}
            {selection_triple}
        }} ORDER BY ?same ?p"""
    else:
        query = f"""
            PREFIX lirb: <https://raw.githubusercontent.com/CaioViktor/LiRB/main/lirb_ontology.ttl/>
            # select ?same ?p ?o where {{ 
            {select}
                {selection_triple}   
                FILTER NOT EXISTS{{
                    ?o a lirb:N_ary_Relation_Class 
                }}
            }} ORDER BY ?same ?p	     
        """
    sparql_resources.setQuery(query)
    # print(query)
    sparql_resources.setReturnFormat(JSON)
    results = sparql_resources.query().convert()
    properties_o = {}
    metadatas = {}
    
    c = 1
    for result in results["results"]["bindings"]:
        print(c, end='. ')
        c += 1
        print(result, end='\n\n')
        if not result['p']['value'] in properties_o:
            properties_o[result['p']['value']] = []
        if EXPAND_SAMEAS == True:
            if 'datatype' in result['o']:
                properties_o[result['p']['value']].append([result['o']['value'], [], [result['same']['value']], result['o']['datatype']])
            else:
                properties_o[result['p']['value']].append([result['o']['value'], [], [result['same']['value'],[]]])
        else:
            print(result['o'], end='\n\n')
            if 'datatype' in result['o']:
                properties_o[result['p']['value']].append([result['o']['value'], [], [result['same']['value']], result['o']['datatype']])
            else:
                properties_o[result['p']['value']].append([result['o']['value'], [], [],[]])
        
       

    selection_triple= f"<{uri}> ?p1 ?o_aux ."
    if EXPAND_SAMEAS:
        selection_triple = f"""
                {{
                    <{uri}> ?p1 ?o_aux .
                    BIND (<{uri}> AS ?same)
                }}
                UNION{{
                    {{
                        <{uri}> owl:sameAs ?same.
                        ?same ?p1 ?o_aux .
                        FILTER(!CONTAINS(STR(?same),"http://www.sefaz.ma.gov.br/resource/App"))
                    }}
                }}
                FILTER(?p != owl:sameAs)
        """
    if USE_N_ARY_RELATIONS:
        query = f"""
            PREFIX lirb: <https://raw.githubusercontent.com/CaioViktor/LiRB/main/lirb_ontology.ttl/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            select ?p1 ?o1 ?p2  ?o2 where {{ 
                {selection_triple}
                ?o_aux a lirb:N_ary_Relation_Class;
                    rdf:objeto_referenciado ?o1;
                    ?p2 ?o2.
                FILTER(!CONTAINS(STR(?p2),"http://www.w3.org/2000/01/rdf-schema#"))
                FILTER(!CONTAINS(STR(?p2),"http://www.w3.org/2001/XMLSchema#"))
                FILTER(!CONTAINS(STR(?p2),"http://www.w3.org/1999/02/22-rdf-syntax-ns#"))
                FILTER(!CONTAINS(STR(?p2),"http://www.w3.org/2002/07/owl#"))
            }}  
        """
        sparql_resources.setQuery(query)
        # print(query)
        sparql_resources.setReturnFormat(JSON)
        results = sparql_resources.query().convert()
        
        for result in results["results"]["bindings"]:
            if not result['p1']['value'] in properties_o:
                properties_o[result['p1']['value']] = []
                metadatas[result['p1']['value']] = {}
            if not result['o1']['value'] in metadatas[result['p1']['value']]:
                metadatas[result['p1']['value']][result['o1']['value']] = []
            metadatas[result['p1']['value']][result['o1']['value']].append([result['p2']['value'],result['o2']['value']])    
        
        for property in metadatas:
            for value in metadatas[property]:
                properties_o[property].append([value,metadatas[property][value],[]])
        
    properties_list = json.loads(properties())['properties']
    classes_list = {}
    for classe in json.loads(classes())['classes']:
        classes_list[classe['uri_raw']] = classe['label']
    return jsonify({'properties':properties_o,'properties_list':properties_list,'classes_list':classes_list,'graphdb_link':GRAPHDB_BROWSER+"?uri="+urllib.parse.quote(uri)+str(GRAPHDB_BROWSER_CONFIG)+"&embedded"})

@app.route("/get_income_properties")
def get_income_properties(methods=['GET']):
    uri = request.args.get('uri',default="")
    
    expand_sameas = request.args.get('expand_sameas',default="False")
    if expand_sameas == "True" :
        EXPAND_SAMEAS = True
    else:
        EXPAND_SAMEAS = False

    selection_triple = f'?s ?p <{uri}>.'
    if EXPAND_SAMEAS:
        selection_triple= f"""
                {{
                    ?s ?p <{uri}>.
                    # BIND(<{uri}> AS ?same)
                }}
                UNION{{
                    {{
                        <{uri}> owl:sameAs ?same.
                        ?s ?p ?same.
                    }}
                    # UNION{{
                    #     ?same owl:sameAs <{uri}>.
                    #     ?s ?p ?same.
                    # }}
                }}
                FILTER(?p != owl:sameAs)
        """
    query = f"""
        SELECT ?same ?s ?p  WHERE{{
            {selection_triple} 
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
        properties[result['p']['value']].append([result['s']['value'],[],[]])
    return jsonify(properties)

@app.route("/get_label")
def getLabel(methods=['GET']):
    uri = request.args.get('uri',default="")
    query = f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            select ?s (MAX(?label) as ?label) where {{ 
                BIND(<{uri}> as ?s)
                ?s rdfs:label ?l.
            
                BIND(COALESCE(?l,?s) AS ?label)
            }} GROUP BY ?s
        """
    sparql_resources.setQuery(query)
    # print(query)
    sparql_resources.setReturnFormat(JSON)
    results = sparql_resources.query().convert()
    if len(results["results"]["bindings"]) > 0:
        label = results["results"]["bindings"][0]['label']['value']
    else:
        label = ""
    return {'label':label}

@app.route("/timeline")
def timeline(methods=['GET']):
    uri = request.args.get('uri',default="")
    expand_sameas = request.args.get('expand_sameas',default="False")
    if expand_sameas == "True" :
        expand_sameas = True
    else:
        expand_sameas = False
    return render_template("timeline.html",uri=uri,expand_sameas=expand_sameas)

@app.route("/get_history")
def get_history():
    uri = request.args.get('uri',default=None)

    expand_sameas = request.args.get('expand_sameas',default="False")
    if expand_sameas == "True" :
        EXPAND_SAMEAS_TIMELINES = True
    else:
        EXPAND_SAMEAS_TIMELINES = False

    selection_triple = f'<{uri}> sfz:tem_timeLine ?tl.'
    if EXPAND_SAMEAS_TIMELINES:
        selection_triple= f"""
        {{
            <{uri}> sfz:tem_timeLine ?tl.
        }}
        UNION{{
            {{
                <{uri}> owl:sameAs ?same.
                ?same sfz:tem_timeLine ?tl.
            }}
            # UNION{{ Comentei esse trecho porque o grafo de links já tem o caminho inverso
            #     ?same owl:sameAs <{uri}>.
            #     ?same sfz:tem_timeLine ?tl.
            # }}
        }}
        FILTER(?p != owl:sameAs)
        """
    #UPDATE PROPERTY
    query = """
    prefix owl: <http://www.w3.org/2002/07/owl#>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix tl: <http://purl.org/NET/c4dm/timeline.owl#>
    prefix sfz: <http://www.sefaz.ma.gov.br/ontology/>
    SELECT ?inst ?date ?field  ?va ?vn WHERE {
        $selection_triple
        ?inst tl:timeLine ?tl;
            sfz:tem_atualizacao ?att;
            tl:atDate ?date.
        ?att a sfz:Atualiza_Propriedade;
            sfz:valor_antigo ?va;
            sfz:valor_novo ?vn;
            sfz:atributo ?field.
    }
    ORDER BY ?date ?field 
    """.replace("$selection_triple",selection_triple)
    sparql_history.setQuery(query)
    # print(query)
    sparql_history.setReturnFormat(JSON)
    results = sparql_history.query().convert()
    resources_history_date = {}
    for result in results["results"]["bindings"]:
        fonte = result['inst']['value'].split("resource/")[1].split("/")[0]
        data = result['date']['value']
        if not data in resources_history_date:
            resources_history_date[data]= {}
        if not result['field']['value'] in resources_history_date[data]:
            resources_history_date[data][result['field']['value']] = []
        if not 'FONTE' in resources_history_date[data]:
            resources_history_date[data]['FONTE'] = [fonte]
        resources_history_date[data][result['field']['value']].append({'previous_value': result['va']['value'],'new_value': result['vn']['value']})
    resources_history_property = {}
    for result in results["results"]["bindings"]:
        fonte = result['inst']['value'].split("resource/")[1].split("/")[0]
        data = result['date']['value']
        propriedade = result['field']['value']
        if not propriedade in resources_history_property:
            resources_history_property[propriedade]= {}
        if not data in resources_history_property[propriedade]:
            resources_history_property[propriedade][data] = []
        # if not 'FONTE' in resources_history_property[propriedade][data]:
            # resources_history_property[propriedade][data]['FONTE'] = [fonte]
        resources_history_property[propriedade][data].append({'fonte':fonte,'previous_value': result['va']['value'],'new_value': result['vn']['value']})

    # INSERT RESOURCE
    query = """
    prefix owl: <http://www.w3.org/2002/07/owl#>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix tl: <http://purl.org/NET/c4dm/timeline.owl#>
    prefix sfz: <http://www.sefaz.ma.gov.br/ontology/>
    SELECT DISTINCT ?inst ?date WHERE {
        $selection_triple
        ?inst tl:timeLine ?tl;
            sfz:tem_atualizacao ?att;
            tl:atDate ?date.
        ?att a sfz:Insere_Tipo.
    }
    """.replace("$selection_triple",selection_triple)
    sparql_history.setQuery(query)
    # print(query)
    sparql_history.setReturnFormat(JSON)
    results = sparql_history.query().convert()
    for ins in results["results"]["bindings"]:
        fonte = ins['inst']['value'].split("resource/")[1].split("/")[0]
        data = ins['date']['value']
        if not data in resources_history_date:
            resources_history_date[data] = {}
        if not 'INS' in resources_history_date[data]:
            resources_history_date[data]['INS'] = []
        if not 'FONTE' in resources_history_date[data]:
            resources_history_date[data]['FONTE'] = [fonte]

    # INSERT Relationship
    query = """
    prefix owl: <http://www.w3.org/2002/07/owl#>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix tl: <http://purl.org/NET/c4dm/timeline.owl#>
    prefix sfz: <http://www.sefaz.ma.gov.br/ontology/>
    SELECT DISTINCT ?inst ?date ?prop ?obj WHERE {
        $selection_triple
        ?inst tl:timeLine ?tl;
            sfz:tem_atualizacao ?att;
            tl:atDate ?date.
        ?att a sfz:Insere_Relacionamento;
            sfz:uri_objeto_relacionado ?obj;
            sfz:atributo ?prop
    }
    """.replace("$selection_triple",selection_triple)
    sparql_history.setQuery(query)
    # print(query)
    sparql_history.setReturnFormat(JSON)
    results = sparql_history.query().convert()
    for ins in results["results"]["bindings"]:
        fonte = ins['inst']['value'].split("resource/")[1].split("/")[0]
        data = ins['date']['value']
        if not data in resources_history_date:
            resources_history_date[data] = {}
        if not 'INS_PROP' in resources_history_date[data]:
            resources_history_date[data]['INS_PROP'] = []
        if not 'FONTE' in resources_history_date[data]:
            resources_history_date[data]['FONTE'] = [fonte]
        resources_history_date[data]['INS_PROP'].append([ins['prop']['value'],ins['obj']['value']])


    # REMOVE RESOURCE
    query = """
    prefix owl: <http://www.w3.org/2002/07/owl#>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix tl: <http://purl.org/NET/c4dm/timeline.owl#>
    prefix sfz: <http://www.sefaz.ma.gov.br/ontology/>
    SELECT DISTINCT ?inst ?date WHERE {
        $selection_triple
        ?inst tl:timeLine ?tl;
            sfz:tem_atualizacao ?att;
            tl:atDate ?date.
        ?att a sfz:Remove_Tipo.
    }
    """.replace("$selection_triple",selection_triple)
    sparql_history.setQuery(query)
    # print(query)
    sparql_history.setReturnFormat(JSON)
    results = sparql_history.query().convert()
    for dell in results["results"]["bindings"]:
        fonte = dell['inst']['value'].split("resource/")[1].split("/")[0]
        data = dell['date']['value']
        if not data in resources_history_date:
            resources_history_date[data] = {}
        if not 'DEL' in resources_history_date[data]:
            resources_history_date[data]['DEL'] = []
        if not 'FONTE' in resources_history_date[data]:
            resources_history_date[data]['FONTE'] = [fonte]

    # REMOVE PROPERTY
    query = """
    prefix owl: <http://www.w3.org/2002/07/owl#>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix tl: <http://purl.org/NET/c4dm/timeline.owl#>
    prefix sfz: <http://www.sefaz.ma.gov.br/ontology/>
    SELECT DISTINCT ?date ?prop ?obj WHERE {
        $selection_triple
        ?inst tl:timeLine ?tl;
            sfz:tem_atualizacao ?att;
            tl:atDate ?date.
        ?att a sfz:Remove_Relacionamento;
            sfz:uri_objeto_relacionado ?obj;
            sfz:atributo ?prop
    }
    """.replace("$selection_triple",selection_triple)
    sparql_history.setQuery(query)
    # print(query)
    sparql_history.setReturnFormat(JSON)
    results = sparql_history.query().convert()
    for ins in results["results"]["bindings"]:
        fonte = ins['inst']['value'].split("resource/")[1].split("/")[0]
        date = ins['date']['value']
        if not date in resources_history_date:
            resources_history_date[date] = {}
        if not 'REM_PROP' in resources_history_date[date]:
            resources_history_date[date]['REM_PROP'] = []
        if not 'FONTE' in resources_history_date[data]:
            resources_history_date[data]['FONTE'] = [fonte]
        resources_history_date[date]['REM_PROP'].append([ins['prop']['value'],ins['obj']['value']])
    
    resources_history_date = dict(sorted(resources_history_date.items()))
    resources = {'resources_history_property':resources_history_property,'resources_history_date':resources_history_date}
    return json.dumps(resources, ensure_ascii=False).encode('utf8')


if __name__ == "__main__":
    # app.run(host='10.33.96.18',port=1111) #Colocar IP da máquina hospedeira (Servidor) aqui
    app.run(host='0.0.0.0',port=2222)
