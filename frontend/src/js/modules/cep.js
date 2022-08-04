const initCep = () => {
    let cep = document.querySelector('#id_zip_code')
    if (cep) {
        cep.addEventListener('blur', (event) => {
            let value = event.target.value
            let cleanedCep = cleanCep(value)
            if (cleanedCep) {
                fetchData(value, fillForm)
            }
        })
    }
}

const cleanCep = (value) => {
    let cep = value.replace(/\D/g, '');
    if (cep != "") {
        let validacep = /^[0-9]{8}$/;
        if (validacep.test(cep)) {
            return cep
        } else {
            setFields(null, '', '', '', '')
        }
    }
    return null
}

const fetchData = (cep_value, callback) => {
    let url = 'https://viacep.com.br/ws/' + cep_value + '/json/'
    let label = document.querySelector('label[for=id_zip_code]')
    fetch(url).
        then((response) => {
            label.innerHTML = 'Cep ' + '<div class="spinner-border spinner-border-sm text-secondary mt-1 ml-2"></div>'
            return response.json()
        }).then((data) => {
            callback(data)
            label.innerHTML = 'Cep'
        }).catch((error) => {
            callback({ erro: true })
            label.innerHTML = 'Cep'
        })
}

const fillForm = (data) => {

    if (data.erro) {
        setFields(null, '', '', '', '')
    } else {
        setFields(
            data.cep,
            data.logradouro,
            data.localidade,
            data.uf
        )
    }
}

const setFields = (zip_code, address, city, state) => {
    if (zip_code) {
        document.querySelector('#id_zip_code').value = zip_code
    }
    document.querySelector('#id_address').value = address
    document.querySelector('#id_city').value = city
    document.querySelector('#id_state').value = state
}


export { initCep }

/* <div id="_status" class="spinner-border spinner-border-sm text-secondary mt-1 ml-2 d-none"></div> */