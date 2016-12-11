$('#searchProduct').click( function () {

    if ($('#searchText').val() == ''){
        return false;
    }


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