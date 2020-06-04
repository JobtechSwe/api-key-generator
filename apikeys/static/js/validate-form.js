

var isJobSearchLicenseApproved = false;
var isJaeLicenseApproved = false;

function approveJobSearchLicense(){
    var domApproveLicense = document.getElementById('approve_licence');
    isJobSearchLicenseApproved = true;
    domApproveLicense.setCustomValidity('');
    if (!domApproveLicense.checked){
        domApproveLicense.click();
    }
}

function approveJobAdEnrichmentsLicense(){
    var domApproveLicense = document.getElementById('approve_licence_jae');
    isJaeLicenseApproved = true;
    domApproveLicense.setCustomValidity('');
    if (!domApproveLicense.checked){
        domApproveLicense.click();
    }
}

function isAnyCheckBoxChecked(ids) {
    var isAnyChecked = false;
    for (var i = 0; i < ids.length; i++){
        var anId = ids[i];
        if (document.getElementById(anId) !== null && document.getElementById(anId).checked) {
            isAnyChecked = true;
            break;
        }
    }
    return isAnyChecked;
}

function isJobSearchOrJobSearchChecked() {
    return isAnyCheckBoxChecked(['jobsearch', 'bulk']);
}


function isAnyApiChecked() {
    return isAnyCheckBoxChecked(['jobsearch', 'bulk', 'tax', 'jae'])
}

var validationMessageJobSearchAgreement = 'Du måste läsa och godkänna avtalet';
var validationMessageJaeAgreement = 'Du måste läsa och godkänna avtalet för JobAd Enrichments';

$(function () {
    $('[data-toggle="tooltip"]').tooltip()
});

$(document).ready(function(){
    document.getElementById('approve_licence').setCustomValidity(validationMessageJobSearchAgreement);
    document.getElementById('approve_licence_jae').setCustomValidity(validationMessageJaeAgreement);


    registerModalEvents('licence', 'agree');
    registerModalEvents('licence_jae', 'agree_jae_btn');
});

function registerModalEvents(modalId, buttonId) {
    var modalJqueryObj = $("#" + modalId);

    var btnAgreeJqueryObj = modalJqueryObj.find( ".btn-agree").first();

    var modalBodyJqueryObj = modalJqueryObj.find(".modal-body").first();
    var domModalBody = modalBodyJqueryObj.get(0);

    var domModal = document.getElementById(modalId);
    // Note: Make sure the approve-button is enabled if there is no scrollbar.
    modalJqueryObj.on('shown.bs.modal', function(){
        // logScrollInfo(domModalBody);
        if(!(domModalBody.clientHeight < domModalBody.scrollHeight)){
            enableAgreeButton(buttonId);
        }
    });
    modalBodyJqueryObj.on('scroll', function(){
        scrollAgreement(domModalBody, buttonId);
    });

}


function scrollAgreement(domModal, buttonId) {
    // logScrollInfo(domModal);

    if(domModal.scrollTop + domModal.offsetHeight >= domModal.scrollHeight){
        // $('#' + buttonId).removeAttr('disabled')
        enableAgreeButton(buttonId);
    }

}

function enableAgreeButton(buttonId) {
    var agreeBtnJqueryObj = $('#' + buttonId);
    agreeBtnJqueryObj.removeAttr('disabled');

    var agreeBtnTooltipWrapperJqueryObj = $('#' + buttonId + '-tooltipwrapper');
    agreeBtnTooltipWrapperJqueryObj.tooltip('dispose');
}



function setAgreementRequired() {
    var searchOrJobSearchChecked = isJobSearchOrJobSearchChecked();
    var domApproveLicense = document.getElementById('approve_licence');

    domApproveLicense.required = searchOrJobSearchChecked;

    if (searchOrJobSearchChecked && (!isJobSearchLicenseApproved || !domApproveLicense.checked)) {
        domApproveLicense.required = true;
        domApproveLicense.setCustomValidity(validationMessageJobSearchAgreement);

    } else {
        domApproveLicense.required = false;
        domApproveLicense.setCustomValidity('');
    }
}

function setAgreementRequiredJae() {
    var apiChecked = isAnyCheckBoxChecked(['jae']);
    var domApproveLicense = document.getElementById('approve_licence_jae');

    domApproveLicense.required = apiChecked;

    if (apiChecked && (!isJaeLicenseApproved || !domApproveLicense.checked)) {
        domApproveLicense.required = true;
        domApproveLicense.setCustomValidity(validationMessageJaeAgreement);

    } else {
        domApproveLicense.required = false;
        domApproveLicense.setCustomValidity('');
    }
}

function checkIfAnyApiChosen() {
    var domJobsearch = document.getElementById('jobsearch');
    if (domJobsearch !== null) {
        if (!isAnyApiChecked()) {
            domJobsearch.setCustomValidity('Du behöver välja minst ett API');
        } else {
            domJobsearch.setCustomValidity('');
        }
    }
}


function logScrollInfo(domModal) {
    // console.log('this.scrollTop+this.offsetHeight:' + (domModal.scrollTop + domModal.offsetHeight) + ', this.scrollHeight:' + domModal.scrollHeight);
    console.log('domModal.clientHeight:' + domModal.clientHeight);
    console.log('domModal.scrollHeight:' + domModal.scrollHeight);
    console.log('domModal.scrollTop:' + domModal.scrollTop);
    console.log('domModal.offsetHeight:' + domModal.offsetHeight);
}

