describe('Authentication E2E Tests', () => {
  beforeEach(() => {
    cy.visit('/login');
  });

  describe('Login Flow', () => {
    it('should display login form', () => {
      cy.get('[data-testid="login-form"]').should('be.visible');
      cy.get('[data-testid="email-input"]').should('be.visible');
      cy.get('[data-testid="password-input"]').should('be.visible');
      cy.get('[data-testid="login-button"]').should('be.visible');
    });

    it('should validate required fields', () => {
      cy.get('[data-testid="login-button"]').click();
      cy.get('[data-testid="email-error"]').should('contain', 'Email is required');
      cy.get('[data-testid="password-error"]').should('contain', 'Password is required');
    });

    it('should validate email format', () => {
      cy.get('[data-testid="email-input"]').type('invalid-email');
      cy.get('[data-testid="password-input"]').type('password123');
      cy.get('[data-testid="login-button"]').click();
      cy.get('[data-testid="email-error"]').should('contain', 'Please enter a valid email');
    });

    it('should login successfully with valid credentials', () => {
      cy.intercept('POST', '/api/v1/auth/login', {
        statusCode: 200,
        body: {
          user: { id: '1', email: 'test@example.com', username: 'testuser' },
          token: 'fake-token'
        }
      }).as('loginRequest');

      cy.get('[data-testid="email-input"]').type('test@example.com');
      cy.get('[data-testid="password-input"]').type('password123');
      cy.get('[data-testid="login-button"]').click();

      cy.wait('@loginRequest');
      cy.url().should('include', '/chat');
      cy.get('[data-testid="user-menu"]').should('contain', 'testuser');
    });

    it('should show error message for invalid credentials', () => {
      cy.intercept('POST', '/api/v1/auth/login', {
        statusCode: 401,
        body: { message: 'Invalid credentials' }
      }).as('loginRequest');

      cy.get('[data-testid="email-input"]').type('test@example.com');
      cy.get('[data-testid="password-input"]').type('wrongpassword');
      cy.get('[data-testid="login-button"]').click();

      cy.wait('@loginRequest');
      cy.get('[data-testid="error-message"]').should('contain', 'Invalid credentials');
    });

    it('should handle network errors gracefully', () => {
      cy.intercept('POST', '/api/v1/auth/login', {
        forceNetworkError: true
      }).as('loginRequest');

      cy.get('[data-testid="email-input"]').type('test@example.com');
      cy.get('[data-testid="password-input"]').type('password123');
      cy.get('[data-testid="login-button"]').click();

      cy.get('[data-testid="error-message"]').should('contain', 'Network error');
    });

    it('should show loading state during login', () => {
      cy.intercept('POST', '/api/v1/auth/login', {
        delay: 1000,
        statusCode: 200,
        body: { user: {}, token: 'fake-token' }
      }).as('loginRequest');

      cy.get('[data-testid="email-input"]').type('test@example.com');
      cy.get('[data-testid="password-input"]').type('password123');
      cy.get('[data-testid="login-button"]').click();

      cy.get('[data-testid="login-button"]').should('be.disabled');
      cy.get('[data-testid="loading-spinner"]').should('be.visible');
    });

    it('should navigate to register page', () => {
      cy.get('[data-testid="register-link"]').click();
      cy.url().should('include', '/register');
    });

    it('should handle forgot password', () => {
      cy.get('[data-testid="forgot-password-link"]').click();
      cy.get('[data-testid="forgot-password-modal"]').should('be.visible');
    });

    it('should support keyboard navigation', () => {
      cy.get('[data-testid="email-input"]').focus();
      cy.get('[data-testid="password-input"]').type('password123');
      cy.get('[data-testid="password-input"]').type('{enter}');
      
      // Should trigger form submission
      cy.get('[data-testid="login-button"]').should('be.disabled');
    });
  });

  describe('Registration Flow', () => {
    beforeEach(() => {
      cy.visit('/register');
    });

    it('should display registration form', () => {
      cy.get('[data-testid="register-form"]').should('be.visible');
      cy.get('[data-testid="email-input"]').should('be.visible');
      cy.get('[data-testid="username-input"]').should('be.visible');
      cy.get('[data-testid="password-input"]').should('be.visible');
      cy.get('[data-testid="confirm-password-input"]').should('be.visible');
      cy.get('[data-testid="full-name-input"]').should('be.visible');
    });

    it('should validate password confirmation', () => {
      cy.get('[data-testid="email-input"]').type('test@example.com');
      cy.get('[data-testid="username-input"]').type('testuser');
      cy.get('[data-testid="password-input"]').type('password123');
      cy.get('[data-testid="confirm-password-input"]').type('differentpassword');
      cy.get('[data-testid="full-name-input"]').type('Test User');
      cy.get('[data-testid="register-button"]').click();

      cy.get('[data-testid="confirm-password-error"]').should('contain', 'Passwords do not match');
    });

    it('should register successfully with valid data', () => {
      cy.intercept('POST', '/api/v1/auth/register', {
        statusCode: 201,
        body: {
          user: { id: '1', email: 'test@example.com', username: 'testuser' },
          token: 'fake-token'
        }
      }).as('registerRequest');

      cy.get('[data-testid="email-input"]').type('test@example.com');
      cy.get('[data-testid="username-input"]').type('testuser');
      cy.get('[data-testid="password-input"]').type('password123');
      cy.get('[data-testid="confirm-password-input"]').type('password123');
      cy.get('[data-testid="full-name-input"]').type('Test User');
      cy.get('[data-testid="register-button"]').click();

      cy.wait('@registerRequest');
      cy.url().should('include', '/chat');
    });

    it('should handle duplicate email error', () => {
      cy.intercept('POST', '/api/v1/auth/register', {
        statusCode: 400,
        body: { message: 'Email already exists' }
      }).as('registerRequest');

      cy.get('[data-testid="email-input"]').type('existing@example.com');
      cy.get('[data-testid="username-input"]').type('existinguser');
      cy.get('[data-testid="password-input"]').type('password123');
      cy.get('[data-testid="confirm-password-input"]').type('password123');
      cy.get('[data-testid="full-name-input"]').type('Existing User');
      cy.get('[data-testid="register-button"]').click();

      cy.wait('@registerRequest');
      cy.get('[data-testid="error-message"]').should('contain', 'Email already exists');
    });
  });

  describe('Logout Flow', () => {
    beforeEach(() => {
      // Login first
      cy.login('test@example.com', 'password123');
    });

    it('should logout successfully', () => {
      cy.intercept('POST', '/api/v1/auth/logout', {
        statusCode: 200,
        body: { message: 'Logged out successfully' }
      }).as('logoutRequest');

      cy.get('[data-testid="user-menu"]').click();
      cy.get('[data-testid="logout-button"]').click();

      cy.wait('@logoutRequest');
      cy.url().should('include', '/login');
      cy.get('[data-testid="login-form"]').should('be.visible');
    });

    it('should clear user data on logout', () => {
      cy.get('[data-testid="user-menu"]').click();
      cy.get('[data-testid="logout-button"]').click();

      // Check that localStorage is cleared
      cy.window().its('localStorage').invoke('getItem', 'user').should('be.null');
      cy.window().its('localStorage').invoke('getItem', 'token').should('be.null');
    });
  });

  describe('Password Reset Flow', () => {
    it('should send password reset email', () => {
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
      cy.get('h2').should('contain', 'Überprüfen Sie Ihre E-Mail');
    });

    it('should validate reset token', () => {
      cy.visit('/reset-password?token=valid-token');
      
      cy.intercept('POST', '/api/v1/auth/validate-reset-token', {
        statusCode: 200,
        body: { 
          valid: true,
          message: 'Token is valid'
        }
      }).as('validateToken');

      cy.wait('@validateToken');
      cy.get('h2').should('contain', 'Passwort zurücksetzen');
    });

    it('should reset password with valid token', () => {
      cy.visit('/reset-password?token=valid-token');
      
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
      }).as('resetPasswordRequest');

      cy.wait('@validateToken');
      cy.get('input[placeholder*="neues Passwort"]').type('NewPassword123!');
      cy.get('input[placeholder*="Bestätigen"]').type('NewPassword123!');
      cy.get('button').contains('Passwort zurücksetzen').click();

      cy.wait('@resetPasswordRequest');
      cy.get('h2').should('contain', 'Passwort-Reset erfolgreich');
    });

    it('should handle invalid token', () => {
      cy.visit('/reset-password?token=invalid-token');
      
      cy.intercept('POST', '/api/v1/auth/validate-reset-token', {
        statusCode: 200,
        body: { 
          valid: false,
          message: 'Token is invalid or expired'
        }
      }).as('validateToken');

      cy.wait('@validateToken');
      cy.get('h2').should('contain', 'Ungültiger Token');
      cy.get('button').contains('Neuen Token anfordern').should('be.visible');
    });
  });

  describe('Social Login', () => {
    it('should handle Google login', () => {
      cy.intercept('GET', '/api/v1/auth/google', {
        statusCode: 302,
        headers: { location: 'https://accounts.google.com/oauth/authorize' }
      }).as('googleAuth');

      cy.get('[data-testid="google-login-button"]').click();
      cy.wait('@googleAuth');
    });

    it('should handle GitHub login', () => {
      cy.intercept('GET', '/api/v1/auth/github', {
        statusCode: 302,
        headers: { location: 'https://github.com/login/oauth/authorize' }
      }).as('githubAuth');

      cy.get('[data-testid="github-login-button"]').click();
      cy.wait('@githubAuth');
    });
  });

  describe('Profile Management', () => {
    beforeEach(() => {
      cy.login('test@example.com', 'password123');
    });

    it('should update user profile', () => {
      cy.visit('/profile');
      
      cy.intercept('PUT', '/api/v1/users/me', {
        statusCode: 200,
        body: {
          id: '1',
          email: 'test@example.com',
          username: 'updateduser',
          fullName: 'Updated Name'
        }
      }).as('updateProfile');

      cy.get('[data-testid="full-name-input"]').clear().type('Updated Name');
      cy.get('[data-testid="username-input"]').clear().type('updateduser');
      cy.get('[data-testid="save-button"]').click();

      cy.wait('@updateProfile');
      cy.get('[data-testid="success-message"]').should('contain', 'Profile updated');
    });

    it('should change password', () => {
      cy.visit('/profile');
      
      cy.intercept('POST', '/api/v1/auth/change-password', {
        statusCode: 200,
        body: { message: 'Password changed successfully' }
      }).as('changePassword');

      cy.get('[data-testid="old-password-input"]').type('oldpassword');
      cy.get('[data-testid="new-password-input"]').type('newpassword123');
      cy.get('[data-testid="confirm-new-password-input"]').type('newpassword123');
      cy.get('[data-testid="change-password-button"]').click();

      cy.wait('@changePassword');
      cy.get('[data-testid="success-message"]').should('contain', 'Password changed');
    });
  });

  describe('Access Control', () => {
    it('should redirect unauthenticated users to login', () => {
      cy.visit('/chat');
      cy.url().should('include', '/login');
    });

    it('should allow authenticated users to access protected routes', () => {
      cy.login('test@example.com', 'password123');
      cy.visit('/chat');
      cy.url().should('include', '/chat');
      cy.get('[data-testid="chat-container"]').should('be.visible');
    });

    it('should handle expired tokens', () => {
      cy.login('test@example.com', 'password123');
      
      // Simulate expired token
      cy.window().its('localStorage').invoke('setItem', 'token', 'expired-token');
      
      cy.visit('/chat');
      cy.url().should('include', '/login');
    });
  });

  describe('Responsive Design', () => {
    it('should work on mobile devices', () => {
      cy.viewport('iphone-x');
      cy.visit('/login');
      
      cy.get('[data-testid="login-form"]').should('be.visible');
      cy.get('[data-testid="email-input"]').should('be.visible');
      cy.get('[data-testid="password-input"]').should('be.visible');
    });

    it('should work on tablet devices', () => {
      cy.viewport('ipad-2');
      cy.visit('/login');
      
      cy.get('[data-testid="login-form"]').should('be.visible');
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      cy.visit('/login');
      
      cy.get('[data-testid="email-input"]').should('have.attr', 'aria-label');
      cy.get('[data-testid="password-input"]').should('have.attr', 'aria-label');
      cy.get('[data-testid="login-button"]').should('have.attr', 'aria-label');
    });

    it('should support keyboard navigation', () => {
      cy.visit('/login');
      
      cy.get('body').tab();
      cy.focus('[data-testid="email-input"]');
      cy.get('[data-testid="email-input"]').should('be.focused');
    });

    it('should have proper focus management', () => {
      cy.visit('/login');
      
      cy.get('[data-testid="email-input"]').focus();
      cy.get('[data-testid="email-input"]').should('be.focused');
      
      cy.get('[data-testid="password-input"]').focus();
      cy.get('[data-testid="password-input"]').should('be.focused');
    });
  });
});