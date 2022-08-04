/**
 * Select the application to execute deposit or withdraw operation
 * The application is selected and the buttons onclick attribute
 * is set to redirect to appropriate operation page.
 */

const selectOperation = () => {

    let select = document.querySelector("#id_select_op")
    let deposit_op = document.querySelector("#id_deposit_op")
    let withdraw_op = document.querySelector("#id_withdraw_op")

    if (select){
        select.addEventListener('change', () => {
            if (select.value){
                deposit_op.disabled = false
                withdraw_op.disabled = false
                let optionDataset = select.options[select.selectedIndex].dataset
                deposit_op.setAttribute('onclick',`window.location.href='${optionDataset.depositUrl}'`)
                withdraw_op.setAttribute('onclick',`window.location.href='${optionDataset.withdrawUrl}'`)

            } else {
                deposit_op.disabled = true
                withdraw_op.disabled = true
                deposit_op.onclick=''
                withdraw_op.onclick=''
            }
        })
    }
}

export { selectOperation }