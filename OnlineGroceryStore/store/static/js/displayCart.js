/**
 * Created by scl on 12/11/16.
 */

function unhide(reqFrom) {
    reqFrom.style.display = 'none';
    document.getElementById('orderCart').style.display="block";

}

function deleteFromCart(reqFrom) {
    var formData = {'pId': reqFrom.dataset.pid};

    $.ajax({url: 'deleteFromCart',
           type:'POST',
           data:formData,
           success:function () {
                        window.location = window.location.href;
           },

           error:function (jqXHR, textStatus, errorThrown) {
                     alert('Something went wrong, try later');
                     return false;
           }
       })

}

function updateCart(reqFrom) {
    if (reqFrom.value < 0){
        reqFrom.setCustomValidity('Must be a +ve integer');
        return false;
    }
    else{
        reqFrom.setCustomValidity('');
    }

    if(reqFrom.value == reqFrom.dataset.quantity){
        return false;
    }

    formData={
        'pId':reqFrom.dataset.pid,
        'quantity': reqFrom.value
    };
    $.ajax({url: 'updateCart',
           type:'POST',
           data:formData,
           success:function () {
                        window.location = window.location.href;
           },

           error:function (jqXHR, textStatus, errorThrown) {
                     alert('Something went wrong, try later');
                     return false;
           }
       })

}
