const data = d3.json("/list_resources/" + page + "?classRDF=" + classRDF + "&search=" + search).then(function (dataR) {
	let data = [];
	dataR.sort((fa, fb) => {
		if (fa.label < fb.label) {
			return -1;
		}
		if (fa.label > fb.label) {
			return 1;
		}
		return 0;
	})
	dataR.forEach(function (d) {
		let context = " - " + d.uri.split("resource/")[1].split("/")[0]
		let row = '<tr>';
		row += '<td><li><a target="_blank" href="/browser?uri=' + d.uri + '">' + d.label + "</a>" + context + "</li></td>";
		row += "</tr>";
		$('#elements > tbody:last-child').append(row);
		data.push(d);
	});
	$("#loading").hide();
	return data;
});


