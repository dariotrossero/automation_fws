class primaryButton {
    constructor(locator) {
        this.locator = locator;
    }

    hover() {
        cy.getIframeBody().find(this.locator, { timeout: 15000 }).should('be.visible').trigger('mouseover');

    }

    disabled() {
        cy.getIframeBody().find(this.locator, { timeout: 15000 }).should('be.disabled')
    }

    enabled() {
        cy.getIframeBody().find(this.locator, { timeout: 15000 }).should('be.enabled')
    }
    click() {
        cy.getIframeBody().find(this.locator, { timeout: 15000 }).should('be.visible').click();        
    }
}
export default primaryButton