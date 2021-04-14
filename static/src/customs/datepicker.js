$("#StartDate, #EndDate");

$("#EndDate").change(function () {
    var startDate = document.getElementById("StartDate").value;
    var endDate = document.getElementById("EndDate").value;
 
    if ((Date.parse(endDate) <= Date.parse(startDate))) {
        alert("End date should be greater than Start date");
        document.getElementById("EndDate").value = "";
    }
});