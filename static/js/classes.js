const data = d3.json("/classes").then(function(dataR){
	let data = [];
	dataR.forEach(function(d){
		
		let row = '<tr>';
		row += '<td><a href="resources/0?classRDF='+d.uri+'">'+d.label+"</a></td>";
		row += "</tr>";
		$('#elements > tbody:last-child').append(row);
		data.push(d);
	});
	return data;
});
