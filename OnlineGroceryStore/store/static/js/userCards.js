/**
 * Created by scl on 11/28/16.
 */
var addCardForm = document.getElementById("cardForm_1");
var submitAddCard = document.getElementById("submitAddCard");
var updateSubmit = document.getElementById("submitUpdateCard")

submitAddCard.addEventListener('click', validateAndSubmitCard);
updateSubmit.addEventListener('click',updateCard);

function  validateAndSubmitCard() {
    cardNum = document.getElementById("cardNumber_1");
    cardName = document.getElementById("nameOnCard_1");
    cardMonth = document.getElementById("expMonth_1");
    cardYear = document.getElementById("expYear_1");
    cardCvv = document.getElementById("cvv_1");
    cardNum.setCustomValidity("");
    cardMonth.setCustomValidity("");
    cardCvv.setCustomValidity("");

    if (isNaN(cardNum.value)){
        cardNum.setCustomValidity("Not a valid card Number");
        return false;
    }

    if(cardNum.value.length != 16) {
        cardNum.setCustomValidity("Enter 16 digit Card number without spaces");
        return false
    }

    if(cardYear.value == new Date().getFullYear() && cardMonth.value < (new Date().getMonth()) + 1){
        cardMonth.setCustomValidity("Adding Expired card Not allowed");
        return false;
    }

    if( isNaN(cardCvv.value)){
        cardCvv.setCustomValidity("Not a valid CVV");
        return false;
    }

    if (cardCvv.value > 999){
        cardCvv.setCustomValidity("Invalid CVV number");
        return false;
    }

    var request = new XMLHttpRequest();
	request.open('POST','/addNewCard',false);
	request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    body = "cardNum=" + cardNum.value +  "&cardName=" + cardName.value + "&cardMonth=" + cardMonth.value + '&cardYear=' + cardYear.value + '&cardCvv=' + cardCvv.value;
	request.send(body);

	if (request.readyState == 4 && request.status == 422) {
	    alert("Trying to add existing card, Not allowed.!");
	    return false;
    }
	else if (request.readyState == 4 && request.status != 200) {
        alert("Something went wrong, Try Later");
        return false;
    }
}

function passData (reqfrom) {

    updateSubmit.dataset.cardId = reqfrom.getAttribute('name');
}

function updateCard() {

    cardNum = document.getElementById("cardNumber_2");
    cardName = document.getElementById("nameOnCard_2");
    cardMonth = document.getElementById("expMonth_2");
    cardYear = document.getElementById("expYear_2");
    cardCvv = document.getElementById("cvv_2");
    cardNum.setCustomValidity("");
    cardMonth.setCustomValidity("");
    cardCvv.setCustomValidity("");

    if (isNaN(cardNum.value)){
        cardNum.setCustomValidity("Not a valid card Number");
        return false;
    }

    if(cardNum.value.length != 16) {
        cardNum.setCustomValidity("Enter 16 digit Card number without spaces");
        return false
    }

    if(cardYear.value == new Date().getFullYear() && cardMonth.value < (new Date().getMonth()) + 1){
        cardMonth.setCustomValidity("Adding Expired card Not allowed");
        return false;
    }

    if( isNaN(cardCvv.value)){
        cardCvv.setCustomValidity("Not a valid CVV");
        return false;
    }

    if (cardCvv.value > 999){
        cardCvv.setCustomValidity("Invalid CVV number");
        return false;
    }

    var request = new XMLHttpRequest();
	request.open('POST','/updateCard',false);
	request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    body = "cardNum=" + cardNum.value +  "&cardName=" + cardName.value + "&cardMonth=" + cardMonth.value + '&cardYear=' + cardYear.value + '&cardCvv=' + cardCvv.value + '&cardId=' + updateSubmit.dataset.cardId;
	request.send(body);

	if (request.readyState == 4 && request.status == 422) {
	    alert("Trying to add existing card, Not allowed.!");
	    return false;
    }
	else if (request.readyState == 4 && request.status != 200) {
        alert("Something went wrong, Try Later");
        return false;
    }

}

function deleteCard(reqFrom) {

    var request = new XMLHttpRequest();
    request.open('POST', '/deleteCard', true);
    request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    body = 'cardId=' + reqFrom.getAttribute('name');

    request.onreadystatechange = function () {

        if (request.readyState == 4 && request.status != 200) {
            alert("Something went wrong, Try Later");
            return false;
        }
        else if (request.readyState == 4 && request.status == 200){
             window.location = window.location.href;
        }
    };

    request.send(body);
}