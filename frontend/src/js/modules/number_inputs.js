import SimpleMaskMoney from 'simple-mask-money'


const decimalInput = () => {
    let decimal_input = document.querySelectorAll(".decimal-input")
    if (decimal_input) {
        decimal_input.forEach((element) => {
            let digits = element.dataset.digits
            SimpleMaskMoney.setMask(`#${element.id}`, {
                fractionDigits: digits,
                cursor: 'end'
            })
        })
    }
}

export { decimalInput }