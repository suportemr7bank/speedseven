/**
 * Handle page content reloading
 * 
 * The response html text is rendered inside elements with page-content class and id
 * The server must identify the ajax request and send only page content to be rendered
 * here in appropriate element.
 * 
 * All response elements must be wrapped as:
 * <div class="page-content" id="some_id">
 *  (response content)
 * </div>
 * 
 * The content is removed from this response and inserted in the page into
 * elements: 
 *
 * <div class="page-content" id="some_id">
 *  (response content replaced here)
 * </div>
 * 
 * The request is sent with "X-Requested-With": "XMLHttpRequest" to signalizes ajax request.
 * 
 */


const initPageLoader = (initializer) => {
    /**
     * Initialize page content loading.
     * 
     * @param initializer  A function called when the page content is loaded to initialize another necessary scripts
     * 
     */

    loadMenu(initializer)
    loadForms(initializer)
    handleNavigation()
}

const handleNavigation = () => {
    /**
     *  Page is reloaded when back / forward browser buttons ar pressed
     * 
     */

    window.addEventListener('popstate', function (e) {
        this.window.location.reload()
    });
}

const loadMenu = (initializer) => {
    /**
     * Add listeners to menu links buttons with page-menu-link class.
     * When clicked, the request is intercepet and a ajax post
     * is made to the link href. Only page content is rendered to the respose.
     * 
     * The page content is proprely rendered by loadPageContent(url)
     * 
     */
    let buttons = document.querySelectorAll('.page-menu-link')
    buttons.forEach(
        button => button.addEventListener(
            'click',
            (e) => {
                e.preventDefault()
                let url = button.href
                loadPageContent(url, initializer)
            })
    )
}

const loadPageContent = (url, initializer) => {
    /**
     * Send request to url and reload page content with response
     */
    if (url) {
        let options = {
            method: "GET",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-Page-Content-Reload": "Active",
            }
        }
        fetch(url, options)
            .then((response) => {
                return response.text();
            })
            .then((html_text) => {
                reloadContent(html_text);
                initializer()
                // Change url after page reloading. Content reloading does not change url
                if (window.history.state !== url) {
                    window.history.pushState(url, null, url);
                }
            });
    }
}

const loadForms = (initializer) => {
    /**
     * Intercept submit and send a ajax post
     * 
     * The form content are rendered withou page reloading
     * After saving, the page are redirected by the browser
     * 
     */
    document.addEventListener('submit', function (event) {
        let target_id = event.target.id
        if (target_id !== 'form_id') {
            return true
        }
        event.preventDefault();
        let formData = new FormData(event.target)
        formData.append('button', event.submitter.value)

        fetch(event.target.action, {
            method: 'POST',
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-Page-Content-Reload": "Active",
            },
            body: formData,
        }).then(function (response) {
            if (response.ok) {
                // Change url before rediracting as the page are not reloaded
                window.history.pushState(response.url, null, response.url);
                return response.text();
            }
            return Promise.reject(response);
        }).then(function (html_text) {
            reloadContent(html_text);
            initializer()
        }).catch(function (error) {
            console.log(error);
        });

        return false
    });
}

function reloadContent(html_text) {
    /**
     * Replace all content in div with pagen-content class and an id
     * with html_text, which is a html reponse from ajax request
     * to some url giving back just the page content, not complete page.
     * 
     * <div class="page-content" id="some_id"> (content) </div>
     * 
     */
     console.log(1)

    let temp_div = document.createElement('div');
    temp_div.innerHTML = html_text;
    let temp_content = temp_div.querySelectorAll('.page-content');
    temp_content.forEach(element => {
        let id = element.id;
        let page_content = document.querySelector("#" + id);
        page_content.innerHTML = element.innerHTML;
        element.remove();
    });
}

export { initPageLoader }