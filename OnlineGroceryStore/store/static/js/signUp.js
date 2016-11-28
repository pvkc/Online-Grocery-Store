var passwd = document.getElementById('Password');
var cnfPasswd = document.getElementById('ConfirmPass');
var submit = document.getElementById('SubmitSignUp');
var zip = document.getElementById('Zipcode');

submit.addEventListener('click', validateFields);


function validateFields(){
	if (passwd.value != cnfPasswd.value){
		cnfPasswd.setCustomValidity("Passwords Don't Match");
		return false;
	}
	else{
		cnfPasswd.setCustomValidity("");
	}

	
	if (isNaN(zip.value)){
		zip.setCustomValidity("Invalid Zipcode");
		return false;
	}
	else{
		zip.setCustomValidity("");
	}

	return true
}