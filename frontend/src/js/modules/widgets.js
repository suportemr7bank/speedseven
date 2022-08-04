
let tv_widget = null

function loadTradeViewTechAnalisys(conatiner_id) {
    if (document.getElementById(conatiner_id)) {
        if (tv_widget) {
            tv_widget = null
        }
        tv_widget = new TradingView.widget(
            {
                "autosize": true,
                "symbol": "NQ1!",
                "interval": "D",
                "timezone": "Etc/UTC",
                "theme": "light",
                "style": "1",
                "locale": "br",
                "toolbar_bg": "#f1f3f6",
                "enable_publishing": false,
                "allow_symbol_change": true,
                "container_id": conatiner_id
            }
        );
    }
}

export { loadTradeViewTechAnalisys }