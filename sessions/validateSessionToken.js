
import { setSessionToken, getSessionToken } from "./tokenManagement.js";

export const validateSession = async (sessionToken) => {
  try {
    console.log("Validating session token...");
    
    const response = await fetch('https://api.topstepx.com/api/Auth/validate', {
      method: 'POST',
      headers: {
        'accept': 'text/plain',
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${sessionToken}`
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    
    if (data.success && data.errorCode === 0) {
      console.log('✅ Token is valid. New token received');
      return data.token;
    } else {
      throw new Error(`Validation failed: ${data.errorMessage || 'Unknown error'}`);
    }
  } catch (error) {
    console.error('❌ Validation error:', error);
    throw error;
  }
};

export const validateCurrentSession = async () => {
  const currentToken = getSessionToken();
  
  if (!currentToken) {
    throw new Error('No session token available');
  }
  
  try {
    const newToken = await validateSession(currentToken);
    setSessionToken(newToken);
    console.log('✅ Session validated and token refreshed');
    return newToken;
  } catch (error) {
    console.error('❌ Session validation failed:', error);
    console.log('Please re-authenticate by running authenticate.js');
    throw error; // Throw the error instead of returning null
  }
};

// Auto-run validation when script is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  validateCurrentSession().catch(console.error);
}