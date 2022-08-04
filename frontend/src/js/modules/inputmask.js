import Inputmask from "inputmask"

const initInputMask = () => {

    let phone = document.querySelector('.phone')
    let cpf = document.querySelector('.cpf')
    let cnpj = document.querySelector('.cnpj')
    let zip_code = document.querySelector('.zip_code')

    if (phone){
        Inputmask({
            mask:'(99) 9999[9]-9999',
            onincomplete: function(){
                let value = phone.inputmask.unmaskedvalue()
                if (value.length == 10){
                    phone.value = Inputmask.format(value, {mask:'(99) 9999-9999'})
                }
            }
        }).mask(phone)
    }
   
    if (cpf){
        Inputmask({mask:'999.999.999-99'}).mask(cpf)
    }

    if (zip_code){
        Inputmask("99999-999").mask(zip_code)
    }

    if (cnpj){
        Inputmask("99.999.999/9999-99").mask(cnpj)
    }
}

export { initInputMask }