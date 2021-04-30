console.log("tabel cookie is here.....");

function saveTableDataToCookie() {
  console.log("I am saving table data to csv");
  var tableData = new Array();
  table = document.getElementById("table-data");
  console.log(table);
  for (var row = 0; row < table.rows.length; row++) {
    var r = new Array();
    for (var col = 0; col < table.rows[row].cells.length; col++) {
      r.push(table.rows[row].cells[col].innerText);
    }
    tableData.push(r);
  }

  var json_str = JSON.stringify(tableData);
  createCookie("mycookie", json_str);
}
