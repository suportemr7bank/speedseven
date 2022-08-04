import Modal from 'bootstrap/js/dist/modal';

const initSignup = () => {
    /**
     * If singup requires approval, shows a modal with approval term
     * and allow submition only if terms are accepted
     */


    let signupForm = document.querySelector('#id_signup_form')
    let term_accept = document.querySelector('#id_term_modal_accept')

    validateNotEmpty();
    
    if (signupForm && term_accept) {

        let modal_submit = document.querySelector('#id_modal_submit')

        /**
        Allow submit from modal only if term_accept input is checked
        */
        term_accept.addEventListener('click', (event) => {
            modal_submit.disabled = !event.target.checked
        })


        signupForm.addEventListener('submit', (event) => {
            let target_id = event.target.id
            // Ignores no signup forms
            if (target_id !== 'id_signup_form') {
                return true
            }

            let acceptTern = event.target.dataset.acceptTerm

            // If no acceptance is required, ignores approval step
            if (acceptTern) {
                // Show modal with agreement terms with a submit button if approval is required
                if (event.submitter.id === 'id_signup_submit') {
                    event.preventDefault()
                    let signuTermModal = document.getElementById('id_signup_term_modal')
                    if (signuTermModal) {
                        let modal = new Modal(signuTermModal)
                        modal.show()
                    }
                    return false

                } else if ((event.submitter.id === 'id_modal_submit')) {
                    // Set the signup form approval field value with modal approval field value
                    let accept = document.querySelector('#id_accept_terms')
                    let modal_accept = document.querySelector('#id_term_modal_accept')
                    accept.checked = modal_accept.checked
                    accept.value = modal_accept.checked
                    modal_accept.checked = false
                    return true
                }
            }
        })
    }
}

function validateNotEmpty() {
    let signupSubmit = document.querySelector('#id_signup_submit');
    if (signupSubmit) {
        let form = document.querySelector('#id_signup_form');
        let elements = form.querySelectorAll('input[type=text], input[type=password]');

        elements.forEach((element) => {

            element.addEventListener('keyup', () => {
                let count = 0;
                elements.forEach((e) => {
                    if (e.value.length !== 0) {
                        count += 1;
                    }
                });
                if (count !== (elements.length)) {
                    signupSubmit.disabled = true;
                } else if (count === elements.length) {
                    signupSubmit.disabled = false;
                }
            });
        });
    }
}

export { initSignup }