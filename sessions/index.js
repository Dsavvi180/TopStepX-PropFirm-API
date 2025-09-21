import * as tokenManagement from './tokenManagement.js';
import { authenticate } from './authenticate.js';
import { validateSession, validateCurrentSession } from './validateSessionToken.js';

// Main session management class
class SessionManager {
  constructor() {
    this.tokenManagement = tokenManagement;
  }

  // Authenticate and get a new session token
  async login() {
    try {
      const token = await authenticate();
      console.log('✅ Login successful');
      return token;
    } catch (error) {
      console.error('❌ Login failed:', error);
      throw error;
    }
  }

  // Validate current session token
  async validateSession() {
    try {
      const token = await validateCurrentSession();
      console.log('✅ Session validated');
      return token;
    } catch (error) {
      console.error('❌ Session validation failed:', error);
      throw error; // Re-throw the error instead of returning null
    }
  }

  // Revalidate existing token (refresh without full authentication)
  async revalidateToken() {
    try {
      const currentToken = this.tokenManagement.getSessionToken();
      if (!currentToken) {
        throw new Error('No session token to revalidate');
      }
      
      console.log('Attempting to revalidate existing token...');
      const newToken = await validateCurrentSession();
      console.log('✅ Token revalidated successfully');
      return newToken;
    } catch (error) {
      console.error('❌ Token revalidation failed:', error);
      throw error;
    }
  }

  // Get current token (with automatic validation and authentication)
  async getValidToken() {
    try {
      // First check if we have a valid token in memory
      let token = this.tokenManagement.getValidToken();
      
      if (token) {
        console.log('Valid token found in memory');
        return token;
      }
      
      // If no valid token in memory, check if we have a stored token
      const storedToken = this.tokenManagement.getSessionToken();
      if (storedToken) {
        console.log('Token found in storage, attempting to revalidate...');
        try {
          // Try to revalidate the existing token first
          token = await validateCurrentSession();
          console.log('✅ Token revalidated successfully');
          return token;
        } catch (error) {
          console.log('❌ Token revalidation failed, will reauthenticate...');
          // Clear the invalid token
          this.tokenManagement.clearSessionToken();
        }
      }
      
      // Only authenticate if no token exists or revalidation failed
      console.log('No valid session token found, authenticating...');
      token = await this.login();
      return token;
    } catch (error) {
      console.error('❌ Failed to get valid token:', error);
      throw error;
    }
  }

  // Clear session
  logout() {
    this.tokenManagement.clearSessionToken();
    console.log('✅ Logged out successfully');
  }

  // Check if user is logged in
  isLoggedIn() {
    return this.tokenManagement.getValidToken() !== null;
  }
}

// Create singleton instance
const sessionManager = new SessionManager();

export {
  sessionManager,
  tokenManagement,
  authenticate,
  validateSession,
  validateCurrentSession
};

// Auto-run login when script is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  sessionManager.getValidToken()
    .then(token => {
      console.log('✅ Session ready, token available: ',token);
    })
    .catch(error => {
      console.error('❌ Session setup failed:', error);
    });
}
