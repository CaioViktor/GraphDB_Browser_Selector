const data = d3.json("/classes").then(function(dataR){
	let data = [];
	dataR.forEach(function(d){
		
		let row = '<tr>';
		row += '<td><li><a href="resources/0?classRDF='+d.uri+'&label='+d.label+'">'+d.label+"</a></li></td>";
		row += "</tr>";
		$('#elements > tbody:last-child').append(row);
		data.push(d);
	});
	$("#loading").hide()
	return data;
});
