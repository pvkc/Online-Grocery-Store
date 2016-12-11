$('#searchProduct').click( function (e) {

    if ($('#searchText').val() == ''){
        return false;
    }

    e.preventDefault();


    formData = { 'searchText':$('#searchText').val(),
        'state': $('#storeState').data('state')
    };


    $.ajax({url: 'searchProduct',
           type:'POST',
           data:formData,
           success:function (data) {
                       // window.location = window.location.href;
               var productDisplay = document.getElementById('productDisplay');
               productDisplay.innerHTML = data;
           },

           error:function (XHR, textStatus, errorThrown) {
                   productDisplay.innerHTML = "Something is wrong, try later."
           }
       })
});

function addToCart(reqFrom) {
    if(reqFrom.parentNode.children.quantity.value < 0){
        //alert('Quantity must be +ve integer');
        reqFrom.parentNode.children.quantity.setCustomValidity('Quantity must be +ve integer');
        return false;
    }
    else{
        reqFrom.parentNode.children.quantity.setCustomValidity('');
    }

    return true;
}