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


