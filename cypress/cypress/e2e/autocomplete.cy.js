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
      cy.visit(Cypress.env('storybook_url'))
    })

    it('testing', () => {
    const FIRST_OPT = 'Therese Wunsch'
    const SECOND_OPT = 'Donald Smith'
    
    cy.getIframeBody().find('button[id="headlessui-combobox-button-:r1:"] span', { timeout: TIMEOUT }).should('be.visible').should('have.text', 'keyboard_arrow_down')
    cy.getIframeBody().find('input[id="headlessui-combobox-input-:r0:"]', { timeout: TIMEOUT }).should('be.visible').type("Th")
    cy.getIframeBody().find('ul[id="headlessui-combobox-options-:r2:"]', { timeout: TIMEOUT }).should('be.visible').find("li").eq(0).should('have.text', FIRST_OPT)
    cy.getIframeBody().find('ul[id="headlessui-combobox-options-:r2:"]', { timeout: TIMEOUT }).should('be.visible').find("li").eq(1).should('have.text', SECOND_OPT)
    cy.getIframeBody().find('button[id="headlessui-combobox-button-:r1:"] span', { timeout: TIMEOUT }).should('be.visible').should('have.text', 'keyboard_arrow_up')
    cy.getIframeBody().find('ul[id="headlessui-combobox-options-:r2:"]', { timeout: TIMEOUT }).should('be.visible').find("li").eq(1).click()
    
})
})  