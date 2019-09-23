

$("#seeAnotherFieldGroup").change(function() {
    if ($(this).val() == "comp") {
        $('#otherFieldGroupDiv').show();
        $('#companyname').attr('required','');
        $('#companyname').attr('data-error', 'This field is required.');
        $('#companyaddress').attr('required','');
        $('#companyaddress').attr('data-error', 'This field is required.');
        $('#tel').attr('required','');
        $('#tel').attr('data-error', 'This field is required.');
        $('#otherFieldGroupDiv2').hide();
        $('#bokadress').removeAttr('required');
        $('#bokadress').removeAttr('data-error');


    } else {
        $('#otherFieldGroupDiv').hide();
        $('#companyname').removeAttr('required');
        $('#companyname').removeAttr('data-error');
        $('#companyaddress').removeAttr('required');
        $('#companyaddress').removeAttr('data-error');
        $('#tel').removeAttr('required');
        $('#tel').removeAttr('data-error');
        $('#otherFieldGroupDiv2').show();
        $('#bokadress').attr('required','');
        $('#bokadress').attr('data-error', 'This field is required.');
    }
});
$("#seeAnotherFieldGroup").trigger("change");