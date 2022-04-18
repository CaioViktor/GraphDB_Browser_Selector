const data = d3.json("/query_saved/"+id+"/"+page).then(function(dataR){
	let data = [];
	dataR.forEach(function(d){
		
		let row = '<tr>';
		row += '<td title="'+d.graphdb_url+'"><a href="'+d.graphdb_url+'">'+d.label+"</a></td>";
		row += "</tr>";
		$('#elements > tbody:last-child').append(row);
		data.push(d);
	});
	return data;
});


