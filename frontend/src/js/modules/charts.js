import ApexCharts from 'apexcharts'

var chart_list = []

function renderChartPanel(selector) {
    if (chart_list) {
        while (chart_list.length > 0) {
            let chart = chart_list.pop()
            // Charts references must be destroyed otherwise errors occurs
            chart.destroy()
        }
    }

    let chart_element = document.querySelector(selector)

    if (chart_element) {

        let charUrl = chart_element.dataset.chartUrl

        let options = {
            method: "GET",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            }
        }

        fetch(charUrl, options)
            .then((response) => {
                return response.json();
            })
            .then((data) => {
                let charts = data['charts']
                let settings = data['settings']
                chart_element.innerHTML = data['template']
                charts.forEach(item => {
                    let element = document.querySelector('#' + item.div_id)
                    if (item.type === 'chart') {
                        if (element) {
                            renderChart(settings, element, item.data)
                        }
                    } else if (item.type === 'card') {
                        element.innerHTML = item.data;
                    }
                })
            }).catch(function (error) {
                let element = document.querySelector('.chart-panel')
                if (element){
                    element.innerHTML = '<p class="alert-warning p-4 w-25" style="border-radius: 5px"> Dashboard não dinspońivel no momento </p>'
                }
            });

        function renderChart(settings, element, data) {
            if (settings.chartlib === 'apexchart') {
                element.innerHTML = ""
                let chart = new ApexCharts(element, data)
                chart.render()
                // Store references to remove when charts is replaced
                chart_list.push(chart)
            }
        }
    }
}

function reloadChartPanel(url, selector) {
    let chart_element = document.querySelector(selector)
    if (chart_element) {
        chart_element.dataset.chartUrl = url
        renderChartPanel(selector)
    }
}

//Used to load different dashboards in the same page
function loadCharButtons() {
    let buttons = document.querySelectorAll('.chart-button')
    buttons.forEach(
        button => button.addEventListener(
            'click',
            (e) => {
                e.preventDefault()
                reloadChartPanel(button.href, '.chart-panel')
                select(button.dataset.chartSelected)
            })
    )
}

function select(id) {
    let elements = document.querySelectorAll('.chart_selected')
    elements.forEach(element => { element.innerHTML = "" })
    let selected_element = document.querySelector("#chart_" + id)
    selected_element.innerHTML = '<i class="bi bi-check-lg text-success"></i>'
}

export { renderChartPanel, reloadChartPanel, loadCharButtons }