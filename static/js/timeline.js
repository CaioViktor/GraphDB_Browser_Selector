const propriedadesDestaque = ['http://www.w3.org/2000/01/rdf-schema#label','http://www.w3.org/1999/02/22-rdf-syntax-ns#type','http://www.w3.org/2000/01/rdf-schema#comment','http://dbpedia.org/ontology/thumbnail','http://xmlns.com/foaf/0.1/thumbnail','http://xmlns.com/foaf/0.1/img','http://www.sefaz.ma.gov.br/ontology/tem_timeLine'];
let propriedades_list = null;
let classes_list = null;
const data = d3.json("/get_historico?uri="+encodeURI(uri)).then(function(dataR){
	let data = dataR;
    

    let content = '<div class="timeline">';
    content+='<div class="timeline__wrap">';
    content+='<div class="timeline__items">';
    for(dataI in dataR['resources_historico_data']){
        let date = new Date(dataI);
        content+='<div class="timeline__item">';
        content+='<div class="timeline__content">';
        content+= '<h2>'+date.toLocaleString('pt-br')+'</h2><ul>';
        for(propriedade in dataR['resources_historico_data'][dataI]){
            let propriedadeTitle = propriedade.replaceAll("/",' / ');
            content+='<li><b>'+propriedadeTitle+'</b></li><ul>';
            dataR['resources_historico_data'][dataI][propriedade].forEach(function(att){
                content+='<li><span style="color:red;">'+att['valor_antigo']+'</span> <i class="fa-solid fa-arrow-right"></i> <span style="color:green;">'+att['valor_novo']+'</span></li>';
            });
            content+='</ul>';
        }
        content+='</ul></div>';
        content+='</div>';
    }
    content+='</div>';
    content+='</div>';
    content+='</div>';
    
    
        
            
            


	$("#loading").hide();
    $('#timeline').append(content);
    timeline(document.querySelectorAll('.timeline'),{
        forceVerticalMode: 600
    });
	return data;
});


