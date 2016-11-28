var submitNewAddress = document.getElementById('addNewAddr');
var modalFormSubmit = document.getElementById('updateNewAddr');
var updateAddrForm = document.getElementById('addrForm_2');

submitNewAddress.addEventListener('click', validateAndSubmit);
modalFormSubmit.addEventListener('click', updateAddress);

function validateAndSubmit()
{
    var streetName = document.getElementById('streetName_1');
    var street = document.getElementById('street_1');
    var aptNum = document.getElementById('aptNum_1');
    var city = document.getElementById('city_1');
    var state = document.getElementById('state_1');
    var zip = document.getElementById('zipCode_1');
    var setDefault = document.getElementById('setDefault_1');

	//console.log('Submit Clicked');
	//console.log(street);
	//console.log(streetName)

	if (streetName.value == '' && street.value == ''){
		street.setCustomValidity("Both Street and StreetName cannot be empty");
		//streetName.setCustomValidity("Both Street and StreetName cannot be empty");
		return false
	}
	else{
		street.setCustomValidity('');
		//streetName.setCustomValidity("");
	}

	if (isNaN(zip.value)){
		zip.setCustomValidity("Invalid Zipcode");
		return false;
	}
	else{
		zip.setCustomValidity("");
	}

	if (setDefault.checked == true){
		valueSetDefault = 'Y';
	}
	else{
		valueSetDefault = 'N';
	}


	var request = new XMLHttpRequest();
	request.open('POST','/addLivingAddress', false);
	request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	var body = "street=" + street.value + '&' + "streetName=" + streetName.value + '&' +'aptNo=' + aptNum.value + '&' + 'city=' + city.value + '&' + 'state=' + state.value + '&' + 'zipCode=' + zip.value + '&' + 'setDefault=' + valueSetDefault ;
	request.send(body);
	console.log(body);

	if (request.readyState == 4 && request.status == 422){
	    alert("Trying to add existing address, Not allowed.!");
	    return false;
    }
	else if (request.readyState == 4 && request.status != 200) {
            alert("Something went wrong, try later");
            return false;
		}
}

function makeDefault(reqFrom) {
    //console.log(reqFrom.getAttribute('name'))
    var request = new XMLHttpRequest();
    request.open('POST', 'setDefaultLiving', true);
    request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

    request.onreadystatechange = function () {
        if(request.readyState == 4 && request.status == 200){
           document.location.reload()
        }
        else if (request.readyState == 4){
            alert("Something went worng, Try later")
        }
    };

    var body = "addrId=" + reqFrom.getAttribute('name');
    request.send(body);
}

function deleteAddress(reqFrom) {
    var request = new XMLHttpRequest();
    request.open('POST', 'deleteLivingAddress', true);
    request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

    request.onreadystatechange = function () {
        if(request.readyState == 4 && request.status == 200){
           document.location.reload()
        }
        else if (request.readyState == 4){
            alert("Something went worng, Try later")
        }
    };

    var body = "addrId=" + reqFrom.getAttribute('name');
    request.send(body);

}

function passData (reqfrom) {
    var streetName = document.getElementById('streetName_2');
    var street = document.getElementById('street_2');
    var aptNum = document.getElementById('aptNum_2');
    var city = document.getElementById('city_2');
    var state = document.getElementById('state_2');
    var zip = document.getElementById('zipCode_2');
    var setDefault = document.getElementById('setDefault_2');

    modalFormSubmit.dataset.addrId = reqfrom.getAttribute('name');
    modalFormSubmit.dataset.street = reqfrom.dataset.street;
    modalFormSubmit.dataset.streetName = reqfrom.dataset.streetName;
    modalFormSubmit.dataset.aptNum = reqfrom.dataset.aptNum;
    modalFormSubmit.dataset.city = reqfrom.dataset.city;
    modalFormSubmit.dataset.state = reqfrom.dataset.state;
    modalFormSubmit.dataset.zip = reqfrom.dataset.zip;

    street.value = reqfrom.dataset.street;
    streetName.value = reqfrom.dataset.streetName;
    aptNum.value = reqfrom.dataset.aptNum;
    city.value = reqfrom.dataset.city;
    state.value = reqfrom.dataset.state;
    zip.value = reqfrom.dataset.zip;
}

function updateAddress() {
    var streetName = document.getElementById('streetName_2');
    var street = document.getElementById('street_2');
    var aptNum = document.getElementById('aptNum_2');
    var city = document.getElementById('city_2');
    var state = document.getElementById('state_2');
    var zip = document.getElementById('zipCode_2');
    var setDefault = document.getElementById('setDefault_2');

    if (
         modalFormSubmit.dataset.street        ==   street.value   &&
         modalFormSubmit.dataset.streetName    ==   streetName.value   &&
         modalFormSubmit.dataset.aptNum        ==   aptNum.value   &&
         modalFormSubmit.dataset.city          ==   city.value &&
         modalFormSubmit.dataset.state         ==   state.value    &&
         modalFormSubmit.dataset.zip           ==   zip.value
    )
    {

        window.alert('Nothing has Changed');
        return false;
    }

    if (streetName.value == '' && street.value == ''){
		street.setCustomValidity("Both Street and StreetName cannot be empty");
		//streetName.setCustomValidity("Both Street and StreetName cannot be empty");
		return false;
	}
	else{
		street.setCustomValidity('');
		//streetName.setCustomValidity("");
	}

	if (isNaN(zip.value)){
		zip.setCustomValidity("Invalid Zipcode");
		return false;
	}
	else{
		zip.setCustomValidity("");
	}

	var request = new XMLHttpRequest();
	request.open('POST','updateLivingAddress', false);
	request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	var body = "street=" + street.value + '&' + "streetName=" + streetName.value + '&' +'aptNo=' + aptNum.value + '&' + 'city=' + city.value + '&' + 'state=' + state.value + '&' + 'zipCode=' + zip.value + '&' + 'addrId=' + modalFormSubmit.dataset.addrId;
	request.send(body);
	console.log(body);
    if (request.readyState == 4 && request.status == 422) {
        alert("Trying to update to Existing address, Not allowed.!!");
        return false;
    }
	else if (request.readyState == 4 && request.status != 200) {
            alert("Something went wrong, try later");
            return false;
		}


}