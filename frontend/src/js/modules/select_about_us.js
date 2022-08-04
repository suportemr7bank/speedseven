// Change tinyMCE text backgroung color only for exibition
// The html code are not changed

const initAboutUsSelector = () => {

    let bkg_color_select = document.querySelector('#id_abt_us_bkg_color')

    if (bkg_color_select) {
        // Set backgroud color according to initial select value
        window.onload = () => {
            selectColor(bkg_color_select)
        }
        // Set backgroud color according to initial select changing
        bkg_color_select.addEventListener('change', () => {
            selectColor(bkg_color_select)
        })
    }
}

function selectColor(bkg_color) {
    // For black background, set font color to white
    // For light grey and white background, set font color to black
    // Affect only visibility, not html tags properties
    // Color superted: black, white and light_grey (#F8F9FA)

    let color_black = '#000000'
    let color_white = '#FFFFFF'
    
    if (bkg_color.value == color_black) {
        tinyMCE.activeEditor.getBody().style.color = color_white
    } else {
        tinyMCE.activeEditor.getBody().style.color = color_black
    }
    tinyMCE.activeEditor.getBody().style.backgroundColor = bkg_color.value
}

export { initAboutUsSelector }