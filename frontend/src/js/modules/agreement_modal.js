import Modal from 'bootstrap/js/dist/modal';

let agreement_accept = null;
let modal_submit = null;
let accept_div = null;

const initAgreementModal = () => {
    /**
     * If singup requires approval, shows a modal with approval term
     * and allow submition only if terms are accepted
     */


    /**
    Allow submit from modal only if term_accept input is checked
    */
    let agreementForm = document.querySelector('#id_agreement_form')

    if (agreementForm) {

        agreement_accept = document.querySelector('#id_agreement_modal_accept')
        modal_submit = document.querySelector('#id_modal_submit')
        accept_div = document.querySelector('#id_modal_accept_div')

        agreement_accept.addEventListener('click', (event) => {
            modal_submit.disabled = !event.target.checked
        })


        agreementForm.addEventListener('submit', (event) => {
            let target_id = event.target.id

            // Ignores no signup forms
            if (target_id !== 'id_agreement_form') {
                return true
            }

            accept_div.style = 'display: block'
            agreement_accept.disabled = false
            agreement_accept.checked = false
            modal_submit.innerHTML = 'Continuar'
            modal_submit.type = 'submit'
            modal_submit.disabled = true

            // Show modal with agreement 
            if (event.submitter.id === 'id_purchase_product') {
                event.preventDefault()
                let agreementModal = document.getElementById('id_agreement_modal')
                if (agreementModal) {
                    let modal = new Modal(agreementModal)
                    let url = event.target.dataset.agreementUrl
                    
                    let extraArgs = event.target.dataset.extraArgs
                    let extraArgsStr = ''
                    if (extraArgs){
                        let ids = extraArgs.split(',')
                        ids.forEach(element => {
                            let value = document.getElementById('id_'+element).value
                            extraArgsStr += '&value='+value
                        });
                    }
                    console.log(extraArgsStr)

                    fetchData(url, agreementModal, event.submitter.dataset.product, extraArgsStr)
                    modal.show()
                }
                return false

            } else if ((event.submitter.id === 'id_modal_submit')) {
                // Set the signup form approval field value with modal approval field value
                let accept = document.querySelector('#id_accept_agreement')
                let modal_accept = document.querySelector('#id_agreement_modal_accept')
                accept.checked = modal_accept.checked
                accept.value = modal_accept.checked
                modal_accept.checked = false
                return true
            }
        })
    }
}

const fetchData = (url, modal, product_id, extraArgsStr) => {

    fetch(url + '?product_id=' + product_id + extraArgsStr)
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            let element = modal.querySelector('.modal-body')
            let title = modal.querySelector('.modal-title')
            let term = modal.querySelector('#id_agreement_term')
            if (data.error) {
                element.innerHTML = data.error
                accept_div.style = 'display: none'
                agreement_accept.disabled = true
                modal_submit.innerHTML = 'Fechar'
                modal_submit.type = 'button'
                modal_submit.disabled = false

            } else {
                element.innerHTML = data.text
                title.innerHTML = 'Contrato ' + data.product.display_text
                if (data.agreement_term) {
                    term.innerHTML = 'Duração de ' + data.agreement_term
                } else {
                    term.innerHTML = 'Prazo indeterminado'
                }
            }
        }).catch(function (error) {
            let element = modal.querySelector('.modal-body')
            element.innerHTML = "Ocoreu um erro ao tentar acessar o contrato. Tente novamente mais tarde."
            accept_div.style = 'display: none'
            agreement_accept.disabled = true
            modal_submit.innerHTML = 'Fechar'
            modal_submit.type = 'button'
            modal_submit.disabled = false
        });
}

export { initAgreementModal }