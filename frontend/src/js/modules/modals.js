// Modals
import Modal from 'bootstrap/js/dist/modal';

function initializeModal() {
    initDocumentModal()
    // initAgreementModal()

    let messageModal =  document.getElementById('message_modal')
    if (messageModal){
        let modal = new Modal(messageModal)
        modal.show()
    }
}

var call = 0

function initAgreementModal() {
    let agreementModal = document.getElementById('agreement_modal')
    if (agreementModal) {
        agreementModal.addEventListener('show.bs.modal', function (event) {
            if (call ===0){
                renderAgreementContent(agreementModal, event)
                handleAcceptButton(agreementModal, event)
            }
            call=1
        })
    }
}

function renderAgreementContent(agreementModal, event) {
    let url = event.relatedTarget.href
    let productId = event.relatedTarget.dataset.productId
    let body = agreementModal.querySelector('.modal-body')
    let title = agreementModal.querySelector('.modal-title')
    fetch(url + "?id=" + productId)
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            title.innerHTML = data.product_name + ' - ' + data.title
            body.innerHTML = data.text
        });
}


const handleAcceptButton = (agreementModal, event) => {

    let acceptButton = agreementModal.querySelector('#agreement_modal_accept_btn_id')
    acceptButton.disabled = true

    let check = agreementModal.querySelector('#agreement_modal_check_id')
    check.checked = false

    check.addEventListener('change', event => {
        let checked = event.currentTarget.checked
        acceptButton.disabled = !checked
    })

    let modalBody = agreementModal.querySelector('.modal-body')

    let url = event.relatedTarget.href
    let productId = event.relatedTarget.dataset.productId

    function evt(event) {
        event.preventDefault();
        let data = new FormData(event.target)
        data.append('product_id', productId)
        let options = {
            method: 'POST', 
            body: data,
        }

        fetch(url, options)
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            modalBody.innerHTML = 'Contrato finalizado com sucesso'
            check.disabled = false
            acceptButton.disabled = false
            document.removeEventListenerr('submit', evt)
            call=0
        }).catch(function (error) {
            modalBody.innerHTML = 'Ocorreu um erro ao processar seu pedido. Por vafor, tente novamente mais tarde.'
        });

        return false
    }
    
    document.addEventListener('submit', evt)



}



/**
 * 
 * Modal to read documento only
 * 
 */

function initDocumentModal() {
    let termModal = document.getElementById('term_modal')
    if (termModal) {
        termModal.addEventListener('show.bs.modal', function (event) {
            let url = event.relatedTarget.href
            renderDocumentContent(termModal, url)
        })
    }
}


function renderDocumentContent(termModal, url) {
    let body = termModal.querySelector('.modal-body')
    let title = termModal.querySelector('.modal-title')

    fetch(url)
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            title.innerHTML = data.product_name + ' - ' + data.title
            body.innerHTML = data.text
        });
}

export { initializeModal }