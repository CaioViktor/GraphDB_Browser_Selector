const propriedadesDestaque = ['http://www.w3.org/2000/01/rdf-schema#label','http://www.w3.org/1999/02/22-rdf-syntax-ns#type','http://www.w3.org/2000/01/rdf-schema#comment'];
let propriedades_list = null;
let classes_list = null;
const data = d3.json("/get_properties?uri="+uri).then(function(dataR){
	let data = dataR;
	
    classes_list = dataR['classes_list'];
    propriedades_list = dataR['propriedades_list'];
    let properties = dataR['properties'];
    
    $("#grafoVisual")[0].href=dataR['graphdb_link'];

    
    if('http://www.w3.org/2000/01/rdf-schema#label' in properties){
        $(".header-table>b").text(properties['http://www.w3.org/2000/01/rdf-schema#label'][0]);
        $("#nav-label").append(properties['http://www.w3.org/2000/01/rdf-schema#label'][0]);
        let row = '<div id="label" class="row">';
        dataR['properties']['http://www.w3.org/2000/01/rdf-schema#label'].forEach(function(d){
            row += '<p title="Título"><b>'+d+'</b></p>';
        });
        row += '</div>';
        $('#propriedades_destaque').append(row);
    }
    
    
    if('http://www.w3.org/2000/01/rdf-schema#comment' in properties){
        let row = '<div id="comment">"';
        dataR['properties']['http://www.w3.org/2000/01/rdf-schema#comment'].forEach(function(d){
            row += '<p>'+d+'</p>';
        });
        row += '"</div>';
        $('#propriedades_destaque').append(row);
    }

    $('#propriedades_destaque').append('<div id="uri"><p title="URI" >'+uri+'</p></div>');

    if('http://www.w3.org/1999/02/22-rdf-syntax-ns#type' in properties){
        let row = '<div id="type">';
        row += '<b title="http://www.w3.org/1999/02/22-rdf-syntax-ns#type">Tipo</b>';
        row += '<div id="types" class="row">'
        dataR['properties']['http://www.w3.org/1999/02/22-rdf-syntax-ns#type'].forEach(function(d){
            row += '<a title="'+d+'" href="/resources/0/?classRDF='+d+'&label='+classes_list[d]+'" id="'+d+'" class="types">'+classes_list[d]+'</a>';
        });
        row += '</div>';
        row += '</div>';
        $('#propriedades_destaque').append(row);
    }

    for(property in dataR['properties']){
        if(!(propriedadesDestaque.includes(property))){
            let row = '<div id="'+property+'">';
            row += '<b title="'+property+'">'+propriedades_list[property]+'</b>';
            row += '<ul>'
            dataR['properties'][property].forEach(function(d){
                if(d.includes('http'))
                    row += '<li><a href="/browser?uri='+d+'">'+d+'</a></li>';
                else
                    row += '<li><p>'+d+'</p></li>';
            });
            row += '</ul>'
            row += '</div>';
            $('#propriedades_geral').append(row);
        }
    }
	$("#loading").hide();
	return data;
});


