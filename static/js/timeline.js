function getContextFromURI(uri) {
    return uri.toString().split("resource/")[1].split("/")[0]
}
APPS_DE_HIGIENIZACAO = ['AppEndereco','AppRazaoSocial','AppNomeFantasia']
FONTES = ['RFB','REDESIM', 'Cadastro_SEFAZ-MA']


const label = d3.json("/get_label?uri="+encodeURI(uri)).then(function(dataR){
    let context = getContextFromURI(uri)
    $("#label_resource")[0].innerHTML=": <b><i>" +dataR.label+"</i></b>";
    $(".header-table>em").text(`contexto: ${APPS_DE_HIGIENIZACAO.includes(context) ? "Visão Higienizada" : context}`);
    return dataR.label
});


const data = d3.json("/get_history?uri="+encodeURI(uri)+"&expand_sameas="+expand_sameas).then(function(dataR){
	let data = dataR;
    
    let count = 0;
    let content = '<div id="timeline_all" class="timeline">';//Timeline for all properties
    content+='<div class="timeline__wrap">';
    content+='<div class="timeline__items">';
    for(dataI in dataR['resources_history_date']){//Loop to get all dates for all properties
        let date = new Date(dataI);
        content+='<div class="timeline__item">';
        content+=`<div class="timeline__content "` 
        let fonte_atual = ''
        let fonte_content = ''
        for(property in dataR['resources_history_date'][dataI]){
            if(property=="FONTE"){ 
                fonte_atual = dataR['resources_history_date'][dataI][property][0]
                fonte_content+= `<span style="margin-left:4px; font-weight: 300; font-size: 0.8rem"> - ${fonte_atual}</span>`
            }
        }
        content+=`style="background-color: ${BACK_COLORS[fonte_atual]} !important;">`;
        content+= '<h2>'+date.toLocaleString('pt-br');
        content += fonte_content;
        content+='</h2><ul>';
        for(property in dataR['resources_history_date'][dataI]){//Loop to get updated properties
            let propertyTitle = processPropertyName(property);
            if(property != "FONTE"){
                if(property=="INS"){ //loop to get the insertions of a resource
                    content+='<li><span style="color:green;">**Inserção de Recurso**</span></li>';
                    count+=1;
                }else if(property=="DEL"){//loop to get the removals of a resource
                    content+='<li><span style="color:red;">**Remoção de Recurso**</span></li>';
                    count+=1;
                }else if(property=="INS_PROP"){
                    content+='<li><span style="color:green;">**Inserção de Relacionamento**</span></li><ul>';
                    dataR['resources_history_date'][dataI][property].forEach(function(att){//loop to get the insertions of a relationship by date
                        let propertyRefTitle = processPropertyName(att[0]);
                        content+='<li><b title="'+att[0]+'">'+propertyRefTitle+'</b>: <span style="color:green;">'+att[1]+'</span></li>';
                        count+=1;
                    });
                    content+='</ul>';
                }else if(property=="REM_PROP"){
                    content+='<li><span style="color:red;">**Remoção de Relacionamento**</span></li><ul>';
                    dataR['resources_history_date'][dataI][property].forEach(function(att){//loop to get the removals of a relationship by date
                        let propertyRefTitle = processPropertyName(att[0]);
                        content+='<li><b title="'+att[0]+'">'+propertyRefTitle+'</b>: <span style="color:red;">'+att[1]+'</span></li>';
                        count+=1;
                    });
                    content+='</ul>';
                }
                else{
                    content+='<li><b title="'+property+'">'+propertyTitle+'</b></li><ul>';
                    dataR['resources_history_date'][dataI][property].forEach(function(att){//loop to get updates for a property
                        content+='<li><span style="color:red;">'+att['previous_value']+'</span> <i class="fa-solid fa-arrow-right"></i> <span style="color:green;">'+att['new_value']+'</span></li>';
                        count+=1;
                    });
                    content+='</ul>';
                }
            }
        }
        content+='</ul></div>';
        content+='</div>';
    }
    content+='</div>';
    content+='</div>';
    content+='</div>';
    
    console.log(`expand_sameas????`, expand_sameas)
    if (expand_sameas == "True") {
        $(".header-table>em").text("contexto: Visão Unificada");
    }
        
    $('#timeline').append(content);
    $('#timeline_filter').append('<option value="timeline_all">All'+' ('+count+')</option>');

    for(property in dataR['resources_history_property']){
        let count = 0;
        let propertyID= property.replaceAll(":","_").replaceAll(",","_").replaceAll("/","_").replaceAll(" ","_").replaceAll(";","").replaceAll("#","").replaceAll(".","_");
        content = '<div id="timeline_'+propertyID+'" class="timeline" style="display:none;">';
        content+='<div class="timeline__wrap">';
        content+='<div class="timeline__items">';
        for(dataI in dataR['resources_history_property'][property]){//Loop para pegar todas as datas para todas as properties
            let date = new Date(dataI);
            content+='<div class="timeline__item" style="background-color: red !important;">';
            content+='<div class="timeline__content" ';
            
            let fonte_atual = ''
            fonte_atual = dataR['resources_history_property'][property][dataI][0].fonte;
            content+=`style="background-color: ${BACK_COLORS[fonte_atual]} !important;">`;
            content+= '<h2>'+date.toLocaleString('pt-br');
            content += `<span style="margin-left:4px; font-weight: 300; font-size: 0.8rem"> - ${fonte_atual}</span>`;
            content+='</h2><ul>';
            dataR['resources_history_property'][property][dataI].forEach(function(att){
                content+='<li><span style="color:red;">'+att['previous_value']+'</span> <i class="fa-solid fa-arrow-right"></i> <span style="color:green;">'+att['new_value']+'</span></li>';
                count+=1;
            });
            content+='</ul></div>';
            content+='</div>';
        }
        content+='</div>';
        content+='</div>';
        content+='</div>';
        $('#timeline').append(content);
        $('#timeline_filter').append('<option value="timeline_'+propertyID+'">'+property+' ('+count+')</option>');
    }
    $("#loading").hide();
    timeline(document.querySelectorAll('.timeline'),{
        forceVerticalMode: 600
    });

    // if (expand_sameas == "True") {
    //     $(".header-table>em").text("contexto: Visão Unificada");
    // }

	return data;
});

function selectTimeline(el){
    $(".timeline").hide();
    $("#"+el.value).show();
}

function processPropertyName(property){
    let split_slash = property.split("/");
    let last_part = (split_slash.length - 1) >= 0 ? (split_slash.length - 1): 0;
    let propertyTitle = split_slash[last_part];
    if(propertyTitle.includes("#")){
        let split_hash = propertyTitle.split("#");
        last_part = (split_hash.length - 1) >= 0 ? (split_hash.length - 1): 0;
        propertyTitle = split_slash[last_part];
    }
    return propertyTitle;
}

BACK_COLORS = {
    'REDESIM':'#d2e4e8',
    'Cadastro_SEFAZ-MA': '#e2f2e7',
    'RFB': '#fcf0e6'
}