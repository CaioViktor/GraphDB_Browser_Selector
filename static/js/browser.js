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
        $(".header-table>b").text(properties['http://www.w3.org/2000/01/rdf-schema#label'][0][0]);
        $("#nav-label").append(properties['http://www.w3.org/2000/01/rdf-schema#label'][0][0]);
        let row = '<div id="label" class="row">';
        dataR['properties']['http://www.w3.org/2000/01/rdf-schema#label'].forEach(function(d){
            row += '<p title="Título"><b>'+d[0]+'</b></p>';
        });
        row += '</div>';
        $('#propriedades_destaque').append(row);
    }
    
    
    if('http://www.w3.org/2000/01/rdf-schema#comment' in properties){
        let row = '<div id="comment">"';
        dataR['properties']['http://www.w3.org/2000/01/rdf-schema#comment'].forEach(function(d){
            row += '<p>'+d[0]+'</p>';
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
            let label = classes_list[d[0]];
            if(!(d[0] in classes_list)){
                label = d[0].split("/");
                label = label[label.length-1];
                label = label.split("#")
                label = label[label.length-1].replace("_"," ");
            }
            row += '<a title="'+d[0]+'" href="/resources/0/?classRDF='+d[0]+'&label='+classes_list[d[0]]+'" id="'+d[0]+'" class="types">'+label+'</a>';
        });
        row += '</div>';
        row += '</div>';
        $('#propriedades_destaque').append(row);
    }

    for(property in dataR['properties']){
        if(!(propriedadesDestaque.includes(property))){
            let row = '<div id="'+property+'">';
            if(property in propriedades_list)
                row += '<b title="'+property+'">'+propriedades_list[property]+'</b>';
            else{
                let label = property.split("/");
                label = label[label.length-1];
                label = label.split("#")
                label = label[label.length-1].replace("_"," ");
                row += '<b title="'+property+'">'+label+'</b>';
            }
            row += '<ul>'
            dataR['properties'][property].forEach(function(d){
                if(d[0].includes('http'))
                    row += '<li><a href="/browser?uri='+d[0]+'">'+d[0]+'</a></li>';
                else
                    row += '<li><p>'+d[0]+'</p></li>';
                if(d[1].length > 0){
                    row += '<ul>'
                    d[1].forEach(function(meta){
                        let label = propriedades_list[meta[0]];
                        if(!(meta[0] in propriedades_list)){
                            label = meta[0].split("/");
                            label = label[label.length-1];
                            label = label.split("#")
                            label = label[label.length-1].replace("_"," ");
                        }
                        row += '<li title="'+meta[0]+'"><b>'+label+':</b><p> '+meta[1]+'</p></li>';
                    });
                    row += '</ul>'
                }
            });
            row += '</ul>'
            row += '</div>';
            $('#propriedades_geral').append(row);
        }
    }
	$("#loading").hide();
	return data;
});


