import primaryButton from '../components/primaryButton'

const resizeObserverLoopErrRe = /^[^(ResizeObserver loop limit exceeded)]/
Cypress.on('uncaught:exception', (err) => {
    /* returning false here prevents Cypress from failing the test */
    if (resizeObserverLoopErrRe.test(err.message)) {
        return false
    }
})

describe('Autocomplete feature', () => {
    const TIMEOUT = 10000
    beforeEach(() => {
      cy.visit(Cypress.env('storybook_url') + "?path=/docs/coderfull-button--buttons")
    }) 

    it('button enabled', () => {
        let locator = "#story--coderfull-button--primary-inner button:nth-child(1)"
        let button = new primaryButton(locator)
        button.enabled()

    })

    it('button disabled' , () => {
        let locator = "#story--coderfull-button--primary-inner button:nth-child(2)"
        let button = new primaryButton(locator)
        button.disabled()
    })
})