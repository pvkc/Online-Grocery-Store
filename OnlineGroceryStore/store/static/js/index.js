var searchInput = document.getElementById("HomeSearch");


searchInput.addEventListener('keyup',getValue);


function getValue(){
		//var value = document.getElementById('HomeSearch').value;
		var displayMenu = document.getElementById("display");
		var predictedList = document.getElementById("PredictedList");
		displayMenu.innerHTML = ''

		predictedList.insertAdjacentHTML('beforeend', '<option>'+ searchInput.value + '</option>' )
		displayMenu.insertAdjacentHTML('beforeend', '<p>' + searchInput.value + '</p>');
	}