// remove messager after timeout
function activateMessages(timeout) {
    window.setTimeout(() => {
        document.querySelectorAll('.toast').forEach(el => el.remove());
    }, timeout)
}

export { activateMessages }