const data = d3.json("/list_resources/"+page+"?classRDF="+classRDF).then(function(dataR){
	let data = [];
	dataR.forEach(function(d){
		
		let row = '<tr>';
		row += '<td><a href="'+d.graphdb_url+'">'+d.label+"</a></td>";
		row += "</tr>";
		$('#elements > tbody:last-child').append(row);
		data.push(d);
	});
	return data;
});

next=function(){
    let new_url = "/consistencia/"+id+"/"+proximo;
    new_url+="?search="+search;
    new_url+="&search_field="+search_field;
    new_url+="&grau="+$("#grau").val();
    window.location.href = new_url;
}

last=function(){
    let new_url = "/consistencia/"+id+"/"+anterior;
    new_url+="?search="+search;
    new_url+="&search_field="+search_field;
    new_url+="&grau="+$("#grau").val();
    window.location.href = new_url;
}
