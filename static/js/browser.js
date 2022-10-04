const propriedadesDestaque = ['http://www.w3.org/2000/01/rdf-schema#label','http://www.w3.org/1999/02/22-rdf-syntax-ns#type','http://www.w3.org/2000/01/rdf-schema#comment'];
let propriedades_list = null;
let classes_list = null;
const data = d3.json("/get_properties?uri="+uri).then(function(dataR){
	let data = dataR;
	// dataR.forEach(function(d){
		
	// 	let row = '<tr>';
	// 	// row += '<td title="'+d.graphdb_url+'"><li><a target="_blank" href="'+d.graphdb_url+'">'+d.label+"</a></li></td>";
	// 	row += '<td><li><a target="_blank" href="/browser?uri='+d.uri+'&label='+d.label+'&classRDF='+classRDF+'&labelClassRDF='+label+'">'+d.label+"</a></li></td>";
	// 	row += "</tr>";
	// 	$('#elements > tbody:last-child').append(row);
	// 	data.push(d);
	// });
    classes_list = dataR['classes_list'];
    propriedades_list = dataR['propriedades_list'];
    for(property in dataR['properties']){
        if(!(propriedadesDestaque.includes(property))){
            let row = '<div id="'+property+'">';
            row += '<h3 title="'+property+'">'+propriedades_list[property]+'</h3>';
            row += '<ul>'
            dataR['properties'][property].forEach(function(d){
                if(d.includes('http'))
                    row += '<li><a href="/browser?uri='+d+'">'+d+'</a></li>';
                else
                    row += '<li>'+d+'</li>';
            });
            row += '</ul>'
            row += '</div>';
            $('#propriedades_geral').append(row);
        }
    }
	$("#loading").hide();
	return data;
});


