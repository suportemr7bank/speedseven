import _, { isNull } from 'lodash'

import "flatpickr/dist/flatpickr"
import "flatpickr/dist/l10n/pt"

import '../scss/app.scss'
import '../scss/theme.scss'

import 'bootstrap'
import { Popover } from 'bootstrap';

import { loadCharButtons, renderChartPanel } from './modules/charts'
import { activateMessages } from './modules/messages'
import { initializeModal } from './modules/modals'
import { initPageLoader } from './modules/page_content_loader'
import { loadTradeViewTechAnalisys } from './modules/widgets'
import { initSignup } from './modules/signup'
import { initAgreementModal } from './modules/agreement_modal'
import { initTermForm } from './modules/term_form'
import { initCep } from './modules/cep'
import { initInputMask } from './modules/inputmask'
import { sendBatchEmail } from './modules/send_batch_mail'
import { selectOperation } from './modules/select_operation'
import { initCheckUnlockButton } from './modules/check-unlock-button'
import { decimalInput } from './modules/number_inputs'
import { initAboutUsSelector } from './modules/select_about_us'

import "./modules/django-flatpickr"

// Must be reloaded
function initializer() {
  renderChartPanel('.chart-panel')
  loadCharButtons()
  loadTradeViewTechAnalisys("technical-analysis")
  activateMessages(3000)
  initializeModal()
  initAgreementModal()
  initTermForm()
  initCep()
  initInputMask()
  sendBatchEmail()
  selectOperation()
  initCheckUnlockButton()
  decimalInput()
  initAboutUsSelector()
}

initializer()
initSignup()

var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
  return new Popover(popoverTriggerEl)
})

let attr = document.currentScript.getAttribute('active')
if (attr === 'true') {
  initPageLoader(initializer)
}
