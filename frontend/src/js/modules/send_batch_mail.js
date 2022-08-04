const sendBatchEmail = () => {

    let element = document.getElementById('id_socket_name')

    if (element && JSON.parse(element.textContent).socket_name === "send_batch_email") {
        connect();
    }
}

function connect() {
    let socket = null;

    socket = new WebSocket("wss://" + window.location.host + "/ws/send-batch-mail/");

    socket.onopen = function (e) {
        // console.log("Successfully connected to the WebSocket.");
    }

    socket.onclose = function (e) {
        // console.log("WebSocket connection closed unexpectedly. Trying to reconnect in 2s...");
        setTimeout(function () {
            // console.log("Reconnecting...");
            connect();
        }, 2000);
    };

    socket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        let _data = data.data
        switch (data.type) {
            case "send_batch_email":
                updateElement(_data.sent.id, _data.sent.value)
                updateStatusElement(_data.status.id, _data.status.value, _data.status.text)
                updateElement(_data.date_finished.id, _data.date_finished.value)
                break;
            default:
                // console.error("Unknown message type!");
                break;
        }
    };

    socket.onerror = function (err) {
        // console.log("WebSocket encountered an error: " + err.message);
        // console.log("Closing the socket.");
        socket.close();
    }
}

const updateElement = (id, value) => {
    let element = document.querySelector('#' + id)
    if (value !== null) {
        element.innerHTML = value
    }
}

const updateStatusElement = (id, value, text) => {
    let element = document.querySelector('#' + id)
    if (element) {
        let spinner = '<div class="text-center"><div class="spinner-border spinner-border-sm" role="status"></div></div>'
        if (value === 'PROC' && element.innerHTML !== spinner) {
            element.innerHTML = spinner
        } else if (value === 'FINI' || value === 'FERR') {
            element.innerHTML = text
        }
    }
}

export { sendBatchEmail }