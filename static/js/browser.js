const propriedadesDestaque = ['http://www.w3.org/2000/01/rdf-schema#label', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'http://www.w3.org/2000/01/rdf-schema#comment', 'http://dbpedia.org/ontology/thumbnail', 'http://xmlns.com/foaf/0.1/thumbnail', 'http://xmlns.com/foaf/0.1/img', 'http://www.sefaz.ma.gov.br/ontology/tem_timeLine'];
let properties_list = null;
let classes_list = null;
let income = null;

APPS_DE_HIGIENIZACAO = ['AppEndereco', 'AppRazaoSocial', 'AppNomeFantasia', 'AppSociedade'];
FONTES = ['RFB', 'REDESIM', 'Cadastro_SEFAZ-MA'];

function getContextFromURI(uri) {
    return uri.toString().split("resource/")[1].split("/")[0]
}

function getIdentifierFromURI(uri) {
    let x = uri.toString().split("/")
    let xx = x[x.length - 1].split("#")
    return xx[xx.length - 1]
}

function exibeContextoQuandoVisãoHigienizada(contexto)  {
    return APPS_DE_HIGIENIZACAO.includes(contexto) ? true : false
}



const data = d3.json("/get_properties?uri=" + encodeURI(uri) + "&expand_sameas=" + expand_sameas).then(function (dataR) {
    let data = dataR;
    console.log(`dataR`, dataR)
    let context = getContextFromURI(uri)
    let cpf_cnpj = getIdentifierFromURI(uri)
    classes_list = dataR['classes_list'];
    properties_list = dataR['properties_list'];
    let properties = dataR['properties'];
    const eh_pessoa_juridica = cpf_cnpj > 11



    $("#visualGraph")[0].href = dataR['graphdb_link'];

    /** ADICIONAR OS CONTEXTOS NO MENU DE CONTEXTOS*/
    let itemsOfContext = `<div class="list-group">`
    let itemcontext = ""
    let titleOfContext = 'Fonte'
    let resourceAppHigienizada = ''
    let temLinkComOutrasFontes = false
    for (property in dataR['properties']) {//Looping for all properties
        if (property == 'http://www.w3.org/2002/07/owl#sameAs') {//Resource has sameAs link
            dataR['properties'][property].forEach(function (d) {
                itemcontext = getContextFromURI(d[0])
                if (APPS_DE_HIGIENIZACAO.includes(itemcontext)) {
                    if (itemcontext == "AppSociedade") {
                        resourceAppHigienizada = "http://www.sefaz.ma.gov.br/resource/AppSociedade/Empresa/" + getIdentifierFromURI(d[0])
                    } else if(itemcontext == "AppRazaoSocial"){
                        resourceAppHigienizada = "http://www.sefaz.ma.gov.br/resource/AppRazaoSocial/Empresa/" + getIdentifierFromURI(d[0])
                    } else {
                        resourceAppHigienizada = "http://www.sefaz.ma.gov.br/resource/AppEndereco/Estabelecimento/" + getIdentifierFromURI(d[0])
                    }
                    itemsOfContext += `<a role="button" title="Contexto Visão Higienizada" href="/browser?uri=${resourceAppHigienizada}" class="btn list-group-item list-group-item-action"><i>Visão <i> <b>Higienizada</b></a>`
                } else {
                    temLinkComOutrasFontes = true
                    itemsOfContext += `<a role="button" title="Contexto ${titleOfContext} ${itemcontext}" href="/browser?uri=${d[0]}" class="btn list-group-item list-group-item-action"><i>Visão da Fonte</i> <b>${itemcontext}</b></a>`
                }
            });
        }
        else {
            resourceAppHigienizada = `http://www.sefaz.ma.gov.br/resource/Cadastro_SEFAZ-MA/Estabelecimento/${getIdentifierFromURI(uri)}`
        }
    }

    /**Só exibir se tiver links same-as com outra(s) fonte(s). */
    console.log(`tem links same-as???`, temLinkComOutrasFontes, context, exibeContextoQuandoVisãoHigienizada(context))
    // if(temLinkComOutrasFontes && !exibeContextoQuandoVisãoHigienizada(context) && expand_sameas == "True"){
    if(temLinkComOutrasFontes && expand_sameas == "True"){
        $("#btn_visao_unificada").hide()
    }else{
        $("#btn_visao_unificada").show()
    }
    itemsOfContext += `</div>`
    $('.modal-body').append(itemsOfContext);


    if ('http://www.sefaz.ma.gov.br/ontology/tem_timeLine' in properties) {//Resource has timeline
        $("#timeline")[0].href = 'timeline?uri=' + encodeURI(uri) + "&expand_sameas=" + expand_sameas;
        $("#timeline").show();
    }


    if (['http://dbpedia.org/ontology/thumbnail', 'http://xmlns.com/foaf/0.1/thumbnail', 'http://xmlns.com/foaf/0.1/img'].some(el => el in properties)) {//Thumbnails
        let row = '<div id="thumbs" class="row">';
        ['http://dbpedia.org/ontology/thumbnail', 'http://xmlns.com/foaf/0.1/thumbnail', 'http://xmlns.com/foaf/0.1/img'].forEach(function (attr) {
            if (attr in dataR['properties']) {
                dataR['properties'][attr].forEach(function (d, idx) {
                    row += '<a href="' + encodeURI(d[0]) + '" target="_blank"><img src="' + d[0] + '" alt="' + d[0] + '" title="' + d[0] + '" class="thumbnail"/></a>';
                });
            }
        });
        row += '</div>';
        $('#highlight_properties').append(row);

    }

    let countLabels = 0
    if ('http://www.w3.org/2000/01/rdf-schema#label' in properties) {//Labels
        $(".header-table>b").text(properties['http://www.w3.org/2000/01/rdf-schema#label'][0][0]);
        $(".header-table>em").text(`contexto: ${APPS_DE_HIGIENIZACAO.includes(context) ? "Visão Higienizada" : context}`);
        $("#nav-label").append(properties['http://www.w3.org/2000/01/rdf-schema#label'][0][0]);
        let row = '<div id="label" class="row"><i class="fa-solid fa-tag" title="Nomes"></i>';
        dataR['properties']['http://www.w3.org/2000/01/rdf-schema#label'].forEach(function (d) {
            row += '<p title="Label"><b>' + d[0] + '</b></p>';
        });
        row += '</div>';
        $('#highlight_properties').append(row);
        countLabels += 1
    }

    if (expand_sameas == "True") {
        $(".header-table>em").text("Contexto: Visão Unificada");
    }

    if ('http://www.w3.org/2000/01/rdf-schema#comment' in properties) {//Comments
        let row = '<div id="comment">"';
        dataR['properties']['http://www.w3.org/2000/01/rdf-schema#comment'].forEach(function (d) {
            row += '<p>' + d[0] + '</p>';
        });
        row += '"</div>';
        $('#highlight_properties').append(row);
    }

    $('#highlight_properties').append('<div id="uri"><p title="URI" ><i class="fa-solid fa-link"></i>' + uri + '</p></div>');//URIss

    let auxLabelOfClasses = []
    if ('http://www.w3.org/1999/02/22-rdf-syntax-ns#type' in properties) {//Types
        let row = '<div id="type">';
        row += '<b title="http://www.w3.org/1999/02/22-rdf-syntax-ns#type">Types</b>';
        row += '<div id="types" class="row">'
        dataR['properties']['http://www.w3.org/1999/02/22-rdf-syntax-ns#type'].forEach(function (d) {

            let label = classes_list[d[0]];
            if (!(d[0] in classes_list)) {
                label = d[0].split("/");
                label = label[label.length - 1];
                label = label.split("#")
                label = label[label.length - 1].replaceAll("_", " ");
            }

            /**Não exibir classes repetidas, principalmente no contexto de Visão Unificada. */
            if (!auxLabelOfClasses.includes(label)) {
                row += '<a title="' + d[0] + '" href="/resources/0/?classRDF=' + encodeURI(d[0]) + '&label=' + classes_list[d[0]] + '" id="' + d[0] + '" class="types">' + label + '</a>';
                auxLabelOfClasses.push(label)
            }
        });
        row += '</div>';
        row += '</div>';
        $('#highlight_properties').append(row);
    }
    let idx_prop = 0;
    for (property in dataR['properties']) {//Others properties
        if (!(propriedadesDestaque.includes(property))) {
            let row = '<div id="' + property + '">';
            if (property in properties_list)//Property has label
                row += '<b title="' + property + '">' + properties_list[property] + ' (' + dataR['properties'][property].length + ') <i class="fa-solid fa-arrow-right"></i></b>';
            else {//Property don't have label
                let label = property.split("/");
                label = label[label.length - 1];
                label = label.split("#")
                label = label[label.length - 1].replaceAll("_", " ");
                row += '<b title="' + property + '">' + label + ' (' + dataR['properties'][property].length + ') <i class="fa-solid fa-arrow-right"></i></b>';
            }
            row += '<ul>'
            let count_value = 0;
            dataR['properties'][property].forEach(function (d) {
                let datatypePropertyContext = ''
                if (count_value == 10)
                    row += "<details><summary>More (" + (dataR['properties'][property].length - count_value) + ")</summary>";


                if (d[0].includes('http')) { //Properties is an objectProperty
                    if (['.png', '.jpeg', '.jpg', '.gif', '.svg', '.ico', '.apng', '.bmp'].some(typ => d[0].includes(typ))) {//Property is a image link
                        row += '<li><a href="' + encodeURI(d[0]) + '" target="_blank"><img src="' + d[0] + '" alt="' + d[0] + '" title="' + d[0] + '" class="thumbnail"/></a></li>';
                    }
                    else {//Properties is another objectProperty
                        /** aqui cortar quando for uma Sociedade e Visão Higienizada  */
                        if (context == "AppSociedade" && property == "http://www.sefaz.ma.gov.br/ontology/tem_sociedade") {
                            let _uri_tem_sociedade = d[0].split(" - ")[0]
                            let _status_sociedade = d[0].split(" - ")[1]
                            row += '<li><a id="link_' + idx_prop + '_' + count_value + '" href="/browser?uri=' + encodeURI(_uri_tem_sociedade) + "&expand_sameas=" + expand_sameas + '">' + _uri_tem_sociedade;
                            row += `<span class="context">${_status_sociedade}</span>`;
                        } else {
                            row += '<li><a id="link_' + idx_prop + '_' + count_value + '" href="/browser?uri=' + encodeURI(d[0]) + "&expand_sameas=" + expand_sameas + '">' + d[0];
                        }


                        /**ADICIONA BOTÃO PARA APLICAÇÃO DE RECOMENDAÇÃO DE ENDEREÇO */
                        const objectPropertyContext = getContextFromURI(d[0])
                        console.log(`<>`, property)
                        // if (((property == "http://www.sefaz.ma.gov.br/ontology/tem_endereco" || property == "http://www.sefaz.ma.gov.br/ontology/tem_endereco_recomendado") && objectPropertyContext == "Cadastro_SEFAZ-MA" && exibeContextoQuandoVisãoHigienizada(context))) {
                        if ((property == "http://www.sefaz.ma.gov.br/ontology/tem_endereco_recomendado" && exibeContextoQuandoVisãoHigienizada(context))) {
                            row += `</a><a class="btn btn-sm" href="http://10.33.96.18:5000/recomendacao/0?cnpj=${cpf_cnpj}" target="_blank" style="margin-left: 8px";>Abrir Aplicação</button></li>`
                        }
                        else if (property == "http://www.sefaz.ma.gov.br/ontology/tem_endereco_recomendado" && objectPropertyContext == "EXTRACAD") {
                            if (eh_pessoa_juridica) {
                                row += `</a><a class="btn btn-sm" href="http://10.33.96.18:5001/recomendacao/PJ/0?cnpj=${cpf_cnpj}" target="_blank" style="margin-left: 8px";>Abrir Aplicação</button></li>`
                            }
                            else { /**ABRIR A APLICAÇÃO DE RECOMENDAÇÃO PARA PESSOA FÍSICA */
                                row += `</a><a class="btn btn-sm" href="http://10.33.96.18:5001/recomendacao/PF/0?cnpj=${cpf_cnpj}" target="_blank" style="margin-left: 8px";>Abrir Aplicação</button></li>`
                            }
                        } 
                        else {
                            row += `</a></li>`;
                        }


                        const current_idx = idx_prop + '_' + count_value;
                        if (USE_LABELS) {
                            label_object = d3.json("/get_label?uri=" + encodeURI(d[0])).then(function (l_obj) {
                                if (l_obj['label'].trim().length > 0)
                                    $('#link_' + current_idx).text(l_obj['label']);
                            });
                        }
                    }
                }
                else {//Properties is a datatypeProperty
                    if (d[3] && d[3].includes('date') || property.includes('data')) { /** Para exibir as data no padrão brasileiro */
                        let date_pt_br = ""
                        if (d[0].includes("-")) { /**O formato na fonte Cadastro vem YYYY-MM-DD HH:mm:ss */
                            date_pt_br = new Date(d[0]).toLocaleDateString('pt-BR')
                        } else { /** No fonte tal vem YYYYMMDD */
                            let year = d[0].slice(0, 4)
                            let month = d[0].slice(4, 6)
                            let day = d[0].slice(6, 8)
                            // console.log(year, month, day)
                            date_pt_br = new Date(Date.UTC(year, month - 1, day, 3, 0, 0)).toLocaleDateString('pt-BR')
                        }
                        row += '<li><p id="link_' + idx_prop + '_' + count_value + '">' + date_pt_br;
                    } else if (d[3] && d[3].includes('http://www.w3.org/2001/XMLSchema#double')) {
                        row += '<li><p id="link_' + idx_prop + '_' + count_value + '">' + parseFloat(d[0]).toFixed(2);
                    }
                    else {
                        row += '<li><p id="link_' + idx_prop + '_' + count_value + '">' + d[0];
                    }


                    /**O d[2][0] contém o objeto da tripla (?s owl:sameAs ?o)*/
                    if (d[2][0] && (exibeContextoQuandoVisãoHigienizada(context) || expand_sameas=="True")) { 
                        /**ADICIONA O CONTEXTO ÀS PROPRIEDADES DE DADOS (expand_sameas==True) */
                        if (d[2][0].includes('http')) {
                            datatypePropertyContext = getContextFromURI(d[2][0])
                            row += `<span class="context">${datatypePropertyContext}</span>`;
                        }
                    }
                    else { /**(expand_sameas==False)*/
                        datatypePropertyContext = getContextFromURI(uri)
                    }

                    /**ADICIONA BOTÃO PARA ABRIR A APLICAÇÃO DE NOME FANTASIA */
                    if (property == "http://www.sefaz.ma.gov.br/ontology/nome_fantasia" && exibeContextoQuandoVisãoHigienizada(context)) {
                        if (datatypePropertyContext == 'Cadastro_SEFAZ-MA') {
                            if (eh_pessoa_juridica) {
                                row += `<a class="btn btn-sm" href="http://10.33.96.18:5003/nome_pj/SIM_NOME_FANTASIA/0?search=${cpf_cnpj}" target="_blank" style="margin-left: 8px";>Abrir Aplicação</button></a>`
                            }
                        }
                        else if (datatypePropertyContext == 'EXTRACAD') {
                            if (!eh_pessoa_juridica) {
                                row += `<a class="btn btn-sm" href="http://10.33.96.18:5003/nome_pf/QUALIDADE_NOME_EXTRACAD_PF/0?search=${cpf_cnpj}" target="_blank" style="margin-left: 8px";>Abrir Aplicação</button></a>`
                            }
                        }
                    }
                    /**ADICIONA BOTÃO PARA ABRIR A APLICAÇÃO DE RAZÃO SOCIAL */
                    console.log(`<contexto>`, context)
                    if (property == "http://www.sefaz.ma.gov.br/ontology/razao_social_recomendada" && exibeContextoQuandoVisãoHigienizada(context)) {
                        console.log(`<datatypePropertyContext> `, datatypePropertyContext)
                        if (datatypePropertyContext == 'AppRazaoSocial') {
                            console.log(`eh pj?? `, eh_pessoa_juridica)
                            if (eh_pessoa_juridica) {
                                row += `<a class="btn btn-sm" href="http://10.33.96.18:5003/razao_social_pj/SIM_RAZAO_SOCIAL_CADSEFAZ/0?search=${cpf_cnpj}" target="_blank" style="margin-left: 8px";>Abrir Aplicação</button></a>`
                            }
                        }
                        else if (datatypePropertyContext == 'EXTRACAD') {
                            if (eh_pessoa_juridica) {
                                row += `<a class="btn btn-sm" href="http://10.33.96.18:5003/razao_social_pj/SIM_RAZAO_SOCIAL_EXTRACAD_PJ/0?search=${cpf_cnpj}" target="_blank" style="margin-left: 8px";>Abrir Aplicação</button></a>`
                            }
                        }
                    }
                    row += `</p></li>`
                }
                const current_idx = idx_prop + '_' + count_value;
                if (USE_LABELS && d[0].includes('http') && (exibeContextoQuandoVisãoHigienizada(context) || expand_sameas == "True")|| property == "http://www.w3.org/2002/07/owl#sameAs") {
                    label_object = d3.json("/get_label?uri=" + encodeURI(d[0])).then(function (l_obj) {
                        if (l_obj['label'].trim().length > 0)
                            $('#link_' + current_idx).text(l_obj['label']);
                        /**ADICIONA O CONTEXTO ÀS PROPRIEDADES DE OBJETO */
                        const objectPropertyContext = getContextFromURI(d[0])
                        $('#link_' + current_idx).append(`<span class="context">${objectPropertyContext}</span>`);
                    });
                }

                if (d[1].length > 0) {//Property has metadata (lirb:N_ary_Relation_Class)
                    row += '<ul>';
                    d[1].forEach(function (meta) {
                        if (meta[0] != 'https://raw.githubusercontent.com/CaioViktor/LiRB/main/lirb_ontology.ttl/value') {
                            let label = properties_list[meta[0]];
                            if (!(meta[0] in properties_list)) {
                                label = meta[0].split("/");
                                label = label[label.length - 1];
                                label = label.split("#")
                                label = label[label.length - 1].replaceAll("_", " ");
                            }
                            row += '<li title="' + meta[0] + '"><b>' + label + ':</b><p> ' + meta[1] + '</p></li>';
                        }
                    });
                    row += '</ul>';
                }
                if (count_value == dataR['properties'][property].length)
                    row += "</details>";
                count_value += 1;
            });


            row += '</ul>';
            row += '</div>';
            idx_prop += 1;
            $('#general_properties').append(row);
        }
    }
    $("#loading").hide();
    income = d3.json("/get_income_properties?uri=" + encodeURI(uri) + "&expand_sameas=" + expand_sameas).then(function (dataR) {
        let idx_prop = 0;
        for (property in dataR) {//Others properties
            let row = '<div id="' + property + '">';
            if (property in properties_list)//Property has label
                row += '<b title="' + property + '"><i class="fa-solid fa-arrow-left"></i> ' + properties_list[property] + '</b> (' + dataR[property].length + ")";
            else {//Property dont have label
                let label = property.split("/");
                label = label[label.length - 1];
                label = label.split("#")
                label = label[label.length - 1].replaceAll("_", " ");
                row += '<b title="' + property + '"><i class="fa-solid fa-arrow-left"></i> ' + label + '</b> (' + dataR[property].length + ")";
            }
            row += '<ul>'
            let count_value = 1;
            dataR[property].forEach(function (d) {
                if (count_value == 10)
                    row += "<details><summary>More (" + (dataR[property].length - count_value) + ")</summary>";

                if (d[0].includes('http')) { //Properties is an objectProperty
                    if (['.png', '.jpeg', '.jpg', '.gif', '.svg', '.ico', '.apng', '.bmp'].some(typ => d[0].includes(typ))) {//Property is a image link
                        row += '<li><a href="' + encodeURI(d[0]) + '" target="_blank"><img src="' + d[0] + '" alt="' + d[0] + '" title="' + d[0] + '" class="thumbnail"/></a></li>';
                    }
                    else {//Properties is another objectProperty
                        row += '<li><a id="link_income_' + idx_prop + '_' + count_value + '" href="/browser?uri=' + encodeURI(d[0]) + "&expand_sameas=" + expand_sameas + '">' + d[0] + '</a></li>';
                        const current_idx = idx_prop + '_' + count_value;
                        if (USE_LABELS) {
                            let sameAsIncomeContext = getContextFromURI(d[0])
                            label_object = d3.json("/get_label?uri=" + encodeURI(d[0])).then(function (l_obj) {
                                if (l_obj['label'].trim().length > 0)
                                    $('#link_income_' + current_idx).text(l_obj['label']);
                                /**ADICIONA O CONTEXTO DA PROPRIEDADE DE OBJETO ENTRANDO */
                                $('#link_income_' + current_idx).append(`<span class="context">${sameAsIncomeContext}</span>`);
                            });
                        }
                    }
                }
                if (count_value == dataR[property].length)
                    row += "</details>";
                count_value += 1;
            });
            row += '</ul>'
            row += '</div>';
            idx_prop += 1;
            $('#income_properties').append(row);
        }
        return dataR;
    });
    return data;
});




