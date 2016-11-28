var email = document.getElementById('inputEmail3');
var passwd = document.getElementById('inputPassword3');
var submit = document.getElementById('logIn');

submit.addEventListener('click', validatePassword);

function validatePassword(){
	var request = new XMLHttpRequest();
	request.open('POST','/validate',false);     
	
	request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	request.send("email="+ email.value +'&' + 'password=' + passwd.value);

	if (request.readyState == 4 && request.status != 200) {
            passwd.setCustomValidity('Email/Password not found');
            return false;
		}
	else{
		passwd.setCustomValidity('');
	}
}
