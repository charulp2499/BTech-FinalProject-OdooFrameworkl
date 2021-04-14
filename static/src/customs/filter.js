function pass_out_year(filter){
              var main_box = document.getElementsByName('main_box');
              for(var i=0; i<main_box.length; i++) {
                var record = main_box[i].getElementsByTagName('div')[0];
                var value = record.textContent || record.innerText;
                // debugger;
                if (value.toUpperCase().indexOf(filter.toUpperCase()) > -1) {
                  main_box[i].style.display = "";
              } else {
                  main_box[i].style.display = "none";
              }
              }
            }
function department(filter){
              var main_box = document.getElementsByName('main_box');
              for(var i=0; i<main_box.length; i++) {
              	var record = main_box[i].getElementsByTagName('small')[0];
              	var value = record.textContent || record.innerText;
                // debugger;
                if (value.toUpperCase().indexOf(filter.toUpperCase()) > -1) {
                	main_box[i].style.display = "";
	            } else {
	                main_box[i].style.display = "none";
	            }
              }
}