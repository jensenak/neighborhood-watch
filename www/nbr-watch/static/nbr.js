$().ready(function() {
  $("#add-button").on("click", addHouse);
  loadHouses();
  setTimeout(loadHouses, 43200);
});

function loadHouses() {
  $("#notifier").text("Fetching List...");
  $("#house-table").empty();
  $.ajax({
    url: "/houses",
    dataType: "json",
    method: "GET",
    success: function (data, status, jqxhr) {
      $.each(data.houses, function(idx, house) {
        tableInsert(house);
      });
      $("#notifier").text('');
    }
  });
}

function tableInsert(house) {
  var row = $("<tr data-id='"+house.house+"'>");
  var addr = $("<td>"+house.addr+"</td>");
  var result = $("<td>"+house.result+"</td>");
  var p = (house.price === null) ? "---" : house.price;
  var price = $("<td>"+p+"</td>");
  var timestamp = moment(house.timestamp, "X");
  var last = $("<td>"+timestamp.format("MMM Do, h a")+"</td>");
  var opts = $("<td>");
  var del = $("<button class='btn btn-xs btn-danger'>Delete</button>");
  var det = $("<button class='btn btn-xs btn-primary'>Details</button>");
  del.on("click", removeHouse);
  det.on("click", detailHouse);
  opts.append(det, del);
  row.append(addr, result, price, last, opts);
  $("#house-table").append(row);
}

function addHouse() {
  $("#notifier").text("Saving House...");
  var address = $("#addr-input").val();
  $("#addr-input").val('');
  $.ajax({
    url: "house/new",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({address: address}),
    success: function (data, status, jqxhr) {
      $("#notifier").text("Updating History...");
      $.get("/run/"+data.house);
      setTimeout(loadHouses, 5000);
    }
  });
}

function removeHouse(){
  house = $(this).parent().parent().data('id');
  $.ajax({
    url: "house/"+house,
    method: "DELETE",
    success: loadHouses
  });
}
function detailHouse(){

}
