/**
 * End-to-End Tests for Password Reset Flow
 * 
 * This test suite covers the complete password reset functionality
 * including all user scenarios, error cases, and security features.
 */

describe('Password Reset Flow', () => {
  beforeEach(() => {
    // Reset any previous state
    cy.clearLocalStorage();
    cy.clearCookies();
  });

  describe('Forgot Password Page', () => {
    it('should display forgot password form correctly', () => {
      cy.visit('/forgot-password');
      
      // Check page elements
      cy.get('h2').should('contain', 'Passwort vergessen?');
      cy.get('input[placeholder*="email"]').should('be.visible');
      cy.get('button').contains('Reset-E-Mail senden').should('be.visible');
      cy.get('button').contains('Zurück zur Anmeldung').should('be.visible');
      
      // Check form validation
      cy.get('input[placeholder*="email"]').should('have.attr', 'required');
    });

    it('should validate email format', () => {
      cy.visit('/forgot-password');
      
      const emailInput = cy.get('input[placeholder*="email"]');
      const submitButton = cy.get('button').contains('Reset-E-Mail senden');
      
      // Test invalid email formats
      const invalidEmails = [
        'invalid-email',
        'test@',
        '@example.com',
        'test..test@example.com',
        'test@example..com'
      ];
      
      invalidEmails.forEach(email => {
        emailInput.clear().type(email);
        submitButton.click();
        cy.contains('Bitte geben Sie eine gültige E-Mail-Adresse ein').should('be.visible');
      });
    });

    it('should require email field', () => {
      cy.visit('/forgot-password');
      
      const submitButton = cy.get('button').contains('Reset-E-Mail senden');
      
      // Submit without email
      submitButton.click();
      cy.contains('E-Mail ist erforderlich').should('be.visible');
      
      // Submit with whitespace only
      cy.get('input[placeholder*="email"]').type('   ');
      submitButton.click();
      cy.contains('E-Mail ist erforderlich').should('be.visible');
    });

    it('should handle successful password reset request', () => {
      cy.visit('/forgot-password');
      
      // Mock successful API response
      cy.intercept('POST', '/api/v1/auth/forgot-password', {
        statusCode: 200,
        body: {
          message: 'If the email address exists, a password reset link has been sent.',
          status: 'success'
        }
      }).as('forgotPasswordRequest');
      
      cy.get('input[placeholder*="email"]').type('test@example.com');
      cy.get('button').contains('Reset-E-Mail senden').click();
      
      cy.wait('@forgotPasswordRequest');
      
      // Should show success state
      cy.get('h2').should('contain', 'Überprüfen Sie Ihre E-Mail');
      cy.contains('Wir haben Ihnen eine E-Mail mit einem Link zum Zurücksetzen Ihres Passworts gesendet.').should('be.visible');
      cy.contains('E-Mail-Anweisungen').should('be.visible');
    });

    it('should handle rate limiting errors', () => {
      cy.visit('/forgot-password');
      
      // Mock rate limiting error
      cy.intercept('POST', '/api/v1/auth/forgot-password', {
        statusCode: 429,
        body: {
          detail: 'Too many password reset requests. Please try again later.'
        }
      }).as('rateLimitError');
      
      cy.get('input[placeholder*="email"]').type('test@example.com');
      cy.get('button').contains('Reset-E-Mail senden').click();
      
      cy.wait('@rateLimitError');
      cy.contains('Too many password reset requests. Please try again later.').should('be.visible');
    });

    it('should handle network errors gracefully', () => {
      cy.visit('/forgot-password');
      
      // Mock network error
      cy.intercept('POST', '/api/v1/auth/forgot-password', {
        forceNetworkError: true
      }).as('networkError');
      
      cy.get('input[placeholder*="email"]').type('test@example.com');
      cy.get('button').contains('Reset-E-Mail senden').click();
      
      cy.wait('@networkError');
      // Should handle error gracefully without crashing
    });

    it('should allow trying different email after success', () => {
      cy.visit('/forgot-password');
      
      // Mock successful API response
      cy.intercept('POST', '/api/v1/auth/forgot-password', {
        statusCode: 200,
        body: {
          message: 'If the email address exists, a password reset link has been sent.',
          status: 'success'
        }
      }).as('forgotPasswordRequest');
      
      cy.get('input[placeholder*="email"]').type('test@example.com');
      cy.get('button').contains('Reset-E-Mail senden').click();
      
      cy.wait('@forgotPasswordRequest');
      
      // Click "Try Different Email" button
      cy.get('button').contains('Andere E-Mail-Adresse versuchen').click();
      
      // Should return to form
      cy.get('h2').should('contain', 'Passwort vergessen?');
      cy.get('input[placeholder*="email"]').should('be.visible');
    });

    it('should navigate back to login', () => {
      cy.visit('/forgot-password');
      
      cy.get('button').contains('Zurück zur Anmeldung').click();
      cy.url().should('include', '/login');
    });

    it('should support keyboard navigation', () => {
      cy.visit('/forgot-password');
      
      const emailInput = cy.get('input[placeholder*="email"]');
      const submitButton = cy.get('button').contains('Reset-E-Mail senden');
      
      // Tab navigation
      emailInput.focus();
      emailInput.should('be.focused');
      
      // Enter key submission
      emailInput.type('test@example.com{enter}');
      // Should attempt form submission
    });
  });

  describe('Reset Password Page', () => {
    it('should validate token on page load', () => {
      // Mock token validation
      cy.intercept('POST', '/api/v1/auth/validate-reset-token', {
        statusCode: 200,
        body: {
          valid: true,
          message: 'Token is valid'
        }
      }).as('validateToken');
      
      cy.visit('/reset-password?token=valid-token-123');
      
      cy.wait('@validateToken');
      cy.get('h2').should('contain', 'Passwort zurücksetzen');
    });

    it('should handle invalid token', () => {
      // Mock invalid token
      cy.intercept('POST', '/api/v1/auth/validate-reset-token', {
        statusCode: 200,
        body: {
          valid: false,
          message: 'Token is invalid or expired'
        }
      }).as('validateInvalidToken');
      
      cy.visit('/reset-password?token=invalid-token');
      
      cy.wait('@validateInvalidToken');
      cy.get('h2').should('contain', 'Ungültiger Token');
      cy.contains('Token abgelaufen oder ungültig').should('be.visible');
      cy.get('button').contains('Neuen Token anfordern').should('be.visible');
    });

    it('should handle missing token', () => {
      // Mock missing token
      cy.intercept('POST', '/api/v1/auth/validate-reset-token', {
        statusCode: 200,
        body: {
          valid: false,
          message: 'Token is invalid or expired'
        }
      }).as('validateMissingToken');
      
      cy.visit('/reset-password');
      
      cy.wait('@validateMissingToken');
      cy.get('h2').should('contain', 'Ungültiger Token');
    });

    it('should validate password requirements', () => {
      // Mock valid token
      cy.intercept('POST', '/api/v1/auth/validate-reset-token', {
        statusCode: 200,
        body: {
          valid: true,
          message: 'Token is valid'
        }
      }).as('validateToken');
      
      cy.visit('/reset-password?token=valid-token-123');
      cy.wait('@validateToken');
      
      const passwordInput = cy.get('input[placeholder*="neues Passwort"]');
      const confirmInput = cy.get('input[placeholder*="Bestätigen"]');
      const submitButton = cy.get('button').contains('Passwort zurücksetzen');
      
      // Test weak passwords
      const weakPasswords = ['123', 'password', 'abc123'];
      
      weakPasswords.forEach(password => {
        passwordInput.clear().type(password);
        confirmInput.clear().type(password);
        submitButton.click();
        cy.contains('Passwort muss mindestens 8 Zeichen lang sein').should('be.visible');
      });
    });

    it('should validate password confirmation', () => {
      // Mock valid token
      cy.intercept('POST', '/api/v1/auth/validate-reset-token', {
        statusCode: 200,
        body: {
          valid: true,
          message: 'Token is valid'
        }
      }).as('validateToken');
      
      cy.visit('/reset-password?token=valid-token-123');
      cy.wait('@validateToken');
      
      const passwordInput = cy.get('input[placeholder*="neues Passwort"]');
      const confirmInput = cy.get('input[placeholder*="Bestätigen"]');
      const submitButton = cy.get('button').contains('Passwort zurücksetzen');
      
      passwordInput.type('NewPassword123!');
      confirmInput.type('DifferentPassword123!');
      submitButton.click();
      
      cy.contains('Passwörter stimmen nicht überein').should('be.visible');
    });

    it('should handle successful password reset', () => {
      // Mock valid token
      cy.intercept('POST', '/api/v1/auth/validate-reset-token', {
        statusCode: 200,
        body: {
          valid: true,
          message: 'Token is valid'
        }
      }).as('validateToken');
      
      // Mock successful password reset
      cy.intercept('POST', '/api/v1/auth/reset-password', {
        statusCode: 200,
        body: {
          message: 'Password reset successfully',
          status: 'success'
        }
      }).as('resetPassword');
      
      cy.visit('/reset-password?token=valid-token-123');
      cy.wait('@validateToken');
      
      const passwordInput = cy.get('input[placeholder*="neues Passwort"]');
      const confirmInput = cy.get('input[placeholder*="Bestätigen"]');
      const submitButton = cy.get('button').contains('Passwort zurücksetzen');
      
      passwordInput.type('NewPassword123!');
      confirmInput.type('NewPassword123!');
      submitButton.click();
      
      cy.wait('@resetPassword');
      cy.get('h2').should('contain', 'Passwort-Reset erfolgreich');
      cy.contains('Ihr Passwort wurde erfolgreich zurückgesetzt').should('be.visible');
    });

    it('should handle password reset failure', () => {
      // Mock valid token
      cy.intercept('POST', '/api/v1/auth/validate-reset-token', {
        statusCode: 200,
        body: {
          valid: true,
          message: 'Token is valid'
        }
      }).as('validateToken');
      
      // Mock failed password reset
      cy.intercept('POST', '/api/v1/auth/reset-password', {
        statusCode: 400,
        body: {
          detail: 'Invalid or expired token'
        }
      }).as('resetPasswordFailed');
      
      cy.visit('/reset-password?token=valid-token-123');
      cy.wait('@validateToken');
      
      const passwordInput = cy.get('input[placeholder*="neues Passwort"]');
      const confirmInput = cy.get('input[placeholder*="Bestätigen"]');
      const submitButton = cy.get('button').contains('Passwort zurücksetzen');
      
      passwordInput.type('NewPassword123!');
      confirmInput.type('NewPassword123!');
      submitButton.click();
      
      cy.wait('@resetPasswordFailed');
      cy.contains('Invalid or expired token').should('be.visible');
    });

    it('should navigate to forgot password from invalid token page', () => {
      // Mock invalid token
      cy.intercept('POST', '/api/v1/auth/validate-reset-token', {
        statusCode: 200,
        body: {
          valid: false,
          message: 'Token is invalid or expired'
        }
      }).as('validateInvalidToken');
      
      cy.visit('/reset-password?token=invalid-token');
      cy.wait('@validateInvalidToken');
      
      cy.get('button').contains('Neuen Token anfordern').click();
      cy.url().should('include', '/forgot-password');
    });

    it('should navigate back to login from success page', () => {
      // Mock valid token
      cy.intercept('POST', '/api/v1/auth/validate-reset-token', {
        statusCode: 200,
        body: {
          valid: true,
          message: 'Token is valid'
        }
      }).as('validateToken');
      
      // Mock successful password reset
      cy.intercept('POST', '/api/v1/auth/reset-password', {
        statusCode: 200,
        body: {
          message: 'Password reset successfully',
          status: 'success'
        }
      }).as('resetPassword');
      
      cy.visit('/reset-password?token=valid-token-123');
      cy.wait('@validateToken');
      
      const passwordInput = cy.get('input[placeholder*="neues Passwort"]');
      const confirmInput = cy.get('input[placeholder*="Bestätigen"]');
      const submitButton = cy.get('button').contains('Passwort zurücksetzen');
      
      passwordInput.type('NewPassword123!');
      confirmInput.type('NewPassword123!');
      submitButton.click();
      
      cy.wait('@resetPassword');
      
      cy.get('button').contains('Zurück zur Anmeldung').click();
      cy.url().should('include', '/login');
    });
  });

  describe('Complete Password Reset Flow', () => {
    it('should complete full password reset flow', () => {
      // Step 1: Request password reset
      cy.visit('/forgot-password');
      
      cy.intercept('POST', '/api/v1/auth/forgot-password', {
        statusCode: 200,
        body: {
          message: 'If the email address exists, a password reset link has been sent.',
          status: 'success'
        }
      }).as('forgotPasswordRequest');
      
      cy.get('input[placeholder*="email"]').type('test@example.com');
      cy.get('button').contains('Reset-E-Mail senden').click();
      cy.wait('@forgotPasswordRequest');
      
      // Step 2: Navigate to reset password page (simulating email link)
      cy.visit('/reset-password?token=valid-token-123');
      
      cy.intercept('POST', '/api/v1/auth/validate-reset-token', {
        statusCode: 200,
        body: {
          valid: true,
          message: 'Token is valid'
        }
      }).as('validateToken');
      
      cy.intercept('POST', '/api/v1/auth/reset-password', {
        statusCode: 200,
        body: {
          message: 'Password reset successfully',
          status: 'success'
        }
      }).as('resetPassword');
      
      cy.wait('@validateToken');
      
      // Step 3: Reset password
      cy.get('input[placeholder*="neues Passwort"]').type('NewPassword123!');
      cy.get('input[placeholder*="Bestätigen"]').type('NewPassword123!');
      cy.get('button').contains('Passwort zurücksetzen').click();
      
      cy.wait('@resetPassword');
      
      // Step 4: Verify success and navigate to login
      cy.get('h2').should('contain', 'Passwort-Reset erfolgreich');
      cy.get('button').contains('Zurück zur Anmeldung').click();
      cy.url().should('include', '/login');
    });

    it('should handle expired token in flow', () => {
      // Step 1: Request password reset
      cy.visit('/forgot-password');
      
      cy.intercept('POST', '/api/v1/auth/forgot-password', {
        statusCode: 200,
        body: {
          message: 'If the email address exists, a password reset link has been sent.',
          status: 'success'
        }
      }).as('forgotPasswordRequest');
      
      cy.get('input[placeholder*="email"]').type('test@example.com');
      cy.get('button').contains('Reset-E-Mail senden').click();
      cy.wait('@forgotPasswordRequest');
      
      // Step 2: Navigate to reset password page with expired token
      cy.visit('/reset-password?token=expired-token');
      
      cy.intercept('POST', '/api/v1/auth/validate-reset-token', {
        statusCode: 200,
        body: {
          valid: false,
          message: 'Token is invalid or expired'
        }
      }).as('validateExpiredToken');
      
      cy.wait('@validateExpiredToken');
      
      // Step 3: Request new token
      cy.get('button').contains('Neuen Token anfordern').click();
      cy.url().should('include', '/forgot-password');
    });
  });

  describe('Accessibility and UX', () => {
    it('should be keyboard accessible', () => {
      cy.visit('/forgot-password');
      
      // Tab through all interactive elements
      cy.get('body').tab();
      cy.get('input[placeholder*="email"]').should('be.focused');
      
      cy.get('body').tab();
      cy.get('button').contains('Reset-E-Mail senden').should('be.focused');
      
      cy.get('body').tab();
      cy.get('button').contains('Zurück zur Anmeldung').should('be.focused');
    });

    it('should have proper ARIA labels', () => {
      cy.visit('/forgot-password');
      
      cy.get('input[placeholder*="email"]').should('have.attr', 'aria-label');
      cy.get('button').contains('Reset-E-Mail senden').should('have.attr', 'aria-label');
    });

    it('should show loading states', () => {
      cy.visit('/forgot-password');
      
      cy.intercept('POST', '/api/v1/auth/forgot-password', {
        delay: 1000,
        statusCode: 200,
        body: {
          message: 'If the email address exists, a password reset link has been sent.',
          status: 'success'
        }
      }).as('slowRequest');
      
      cy.get('input[placeholder*="email"]').type('test@example.com');
      cy.get('button').contains('Reset-E-Mail senden').click();
      
      // Should show loading state
      cy.get('button').contains('Reset-E-Mail senden').should('be.disabled');
      
      cy.wait('@slowRequest');
    });

    it('should handle form resubmission prevention', () => {
      cy.visit('/forgot-password');
      
      cy.intercept('POST', '/api/v1/auth/forgot-password', {
        statusCode: 200,
        body: {
          message: 'If the email address exists, a password reset link has been sent.',
          status: 'success'
        }
      }).as('forgotPasswordRequest');
      
      cy.get('input[placeholder*="email"]').type('test@example.com');
      cy.get('button').contains('Reset-E-Mail senden').click();
      
      cy.wait('@forgotPasswordRequest');
      
      // Should prevent resubmission
      cy.get('button').contains('Reset-E-Mail senden').should('not.exist');
    });
  });
});