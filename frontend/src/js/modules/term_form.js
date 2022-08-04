const initTermForm = () => {

    let term_accept = document.querySelector('#id_accept_term')
    let button = document.querySelector('#id_accept_term_button')

    if (term_accept && button){
        term_accept.addEventListener('click', (event) => {
            button.disabled = !event.target.checked
        })
    }
}

export { initTermForm }