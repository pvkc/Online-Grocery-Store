/**
 * Created by scl on 12/8/16.
 */

var oldFormData;
function passWHouseData(reqFrom) {
    submitAddStock.dataset.wid =  reqFrom.dataset.wid
}

$('#submitAddStock').click(function (e) {


    if ($('#quantity_3').val() < 0){
        alert('Must be a Positive integer');
        return false;
    }

     if($('#quantity_3')[0].checkValidity()){}
        else{return ;}

    e.preventDefault();
    e.stopPropagation();

    formData ={
        'pId':$('#productName_3').val(),
        'wId':$(this).data('wid'),
        'quantity':$('#quantity_3').val()
    };



    $.ajax({url: 'addStockWHouse',
           type:'POST',
           data:formData,
           success:function () {
                        window.location = window.location.href;
           },

           error:function (XHR, textStatus, errorThrown) {
                    if (XHR.status == 422){
                     alert('Quantity exceeds Ware House capacity');
                     return false;
                    }
                    else{
                     alert('Something went wrong, try later');
                     return false;
                    }
           }
       })

});

function deleteProduct(reqFrom) {
    var formData = {
      'pId':reqFrom.getAttribute('name'),
       'pstate':reqFrom.dataset.pstate
    };

       $.ajax({url: 'deleteProduct',
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

$('#submitUpdateProduct').click(
    function (e) {

        if($('#product_2')[0].checkValidity()){}
        else{return ;}

        if ($('#product_2').serialize() == oldFormData){
            alert('Nothing Changed');
            return false;
        }

        e.preventDefault();
        e.stopPropagation();

        var formData = {
            'pname':$('#productName_2').val(),
            'pcategory':$('#productCategory_2').val(),
            'psize':$('#productSize_2').val(),
            'padditionalinfo':$('#additionalInfo_2').val(),
            'pstate':$('#stateName_2').val(),
            'oldPState':$(this).data('pstate'),
            'pimagelocation':$('#imageLocation_2').val(),
            'pprice':$('#price_2').val(),
            'priceunit':$("input[name=priceUnit_2]:checked").val(),
            'pId':  $(this).data('pId')
        };

        $.ajax({url: 'updateProduct',
            type:'POST',
            data:formData,
            success:function () {
                         window.location = window.location.href;
            },

            error:function (jqXHR, textStatus, errorThrown) {
                    if(textStatus==422) {
                        alert('Trying to add existing data, Not allowed.!!');
                    }
                    else{
                      alert('Something went wrong, try later');
                      return false;
                    }
            }
        })


    }

);

$('#submitAddProduct').click(
    function (e) {

        if($('#product_1')[0].checkValidity()){}
        else{return ;}

        e.preventDefault();
        e.stopPropagation();

        var formData = {
            'pname':$('#productName_1').val(),
            'pcategory':$('#productCategory_1').val(),
            'psize':$('#productSize_1').val(),
            'padditionalinfo':$('#additionalInfo_1').val(),
            'pstate':$('#stateName_1').val(),
            'pimagelocation':$('#imageLocation_1').val(),
            'pprice':$('#price_1').val(),
            'priceunit':$("input[name=priceUnit_1]:checked").val()
        };

                 $.ajax({url: 'addProduct',
                         type:'POST',
                         data:formData,
                         success:function () {
                                      window.location = window.location.href;
                         },
                         error:function () {
                                   alert('Something went wrong, try later');
                                   return false;
                         }
                 })
    }
);

function passDataToForm(reqFrom) {
    $('#productName_2').val(reqFrom.dataset.pname);
    $('#productCategory_2').val(reqFrom.dataset.pcategory);
    $('#productSize_2').val(reqFrom.dataset.psize);
    $('#additionalInfo_2').val(reqFrom.dataset.padditionalinfo);
    $('#stateName_2').val(reqFrom.dataset.pstate);
    $('#imageLocation_2').val(reqFrom.dataset.pimagelocation);
    $('#price_2').val(reqFrom.dataset.pprice);
    $("input[name=priceUnit_2]").val([reqFrom.dataset.priceunit]);


    $('#submitUpdateProduct').data('pname', reqFrom.dataset.pname);
    $('#submitUpdateProduct').data('pcategory', reqFrom.dataset.pcategory);
    $('#submitUpdateProduct').data('psize',  reqFrom.dataset.psize);
    $('#submitUpdateProduct').data('paddtionalinfo', reqFrom.dataset.paddtionalinfo);
    $('#submitUpdateProduct').data('pstate',  reqFrom.dataset.pstate);
    $('#submitUpdateProduct').data('pimagelocation', reqFrom.dataset.pimagelocation);
    $('#submitUpdateProduct').data('pprice', reqFrom.dataset.pprice);
    $('#submitUpdateProduct').data('priceunit', reqFrom.dataset.priceunit);
    $('#submitUpdateProduct').data('pId',reqFrom.getAttribute('name') );

    oldFormData = $('#product_2').serialize();

    /*
    $('#submitAddProduct').dataset.pname            = reqFrom.dataset.pname;
    $('#submitAddProduct').dataset.pcategory        = reqFrom.dataset.pcategory;
    $('#submitAddProduct').dataset.psize            = reqFrom.dataset.psize;
    $('#submitAddProduct').dataset.paddtionalinfo   = reqFrom.dataset.paddtionalinfo;
    $('#submitAddProduct').dataset.pstate           = reqFrom.dataset.pstate;
    $('#submitAddProduct').dataset.pimagelocation   = reqFrom.dataset.pimagelocation;
    $('#submitAddProduct').dataset.pprice           = reqFrom.dataset.pprice;
    $('#submitAddProduct').dataset.priceunit        = reqFrom.dataset.priceunit;
    */
}