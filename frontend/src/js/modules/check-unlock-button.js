const initCheckUnlockButton = () => {

    let check = document.querySelector('.check-unlock-button')
    
    if (check){

        let value = check.dataset.buttonValue
        
        let button = document.querySelector(`button[value="${value}"]`)
        
        check.addEventListener('click', (event) => {
            button.disabled = !event.target.checked
        })
    }
}

export { initCheckUnlockButton }