/**
 * Created by scl on 12/7/16.
 */
var staffId = document.getElementById('staffId');
var logIn = document.getElementById('logIn');
var passwd = document.getElementById('password');

logIn.addEventListener('click',validateStaffId);

function validateStaffId() {

    if (isNaN(staffId.value)){
        staffId.setCustomValidity('Invalid StaffId');
        return false;
    }
    else{
        var x = parseFloat(value);
        if ((x | 0) === x){
            staffId.setCustomValidity('Invalid StaffId');
            return false;
        }
        staffId.setCustomValidity('');
    }

    var request = new XMLHttpRequest();
	request.open('POST','/staffValidate',false);

	request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	request.send("staffId="+ staffId.value +'&' + 'password=' + passwd.value);

	if (request.readyState == 4 && request.status != 200) {
            passwd.setCustomValidity('StaffId/Password not found');
            return false;
		}
	else{
		passwd.setCustomValidity('');
	}

}
