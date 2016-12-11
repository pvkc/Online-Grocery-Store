var passwd = document.getElementById('Password');
var cnfPasswd = document.getElementById('ConfirmPass');
var submit = document.getElementById('SubmitSignUp');
var zip = document.getElementById('Zipcode');
var email = document.getElementById('EmailId');
var street = document.getElementById('Street');
var streetName = document.getElementById('StreetName');

submit.addEventListener('click', validateFields);


function validateFields(){
	if (passwd.value != cnfPasswd.value){
		cnfPasswd.setCustomValidity("Passwords Don't Match");
		return false;
	}
	else{
		cnfPasswd.setCustomValidity("");
	}

	if(street.value == '' && streetName.value == '')
    {
        street.setCustomValidity('Both Street and Street Names cannot be empty');
    }
    else{
	    street.setCustomValidity('');
    }
	
	if (isNaN(zip.value)){
		zip.setCustomValidity("Invalid Zipcode");
		return false;
	}
	else{
		zip.setCustomValidity("");
	}

    var request = new XMLHttpRequest();
	request.open('POST','/validateEmail',false);

	request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	request.send("email="+ email.value );

	if (request.readyState == 4 && request.status != 200) {
            email.setCustomValidity('Email already in the database');
            return false;
		}
	else{
		email.setCustomValidity('');
	}

	return true
}