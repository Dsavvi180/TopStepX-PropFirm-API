import { setSessionToken } from "./tokenManagement.js";

const API_KEY = 'B+foP4z0KHP73v5m3Cfr7UL2AKN6REgI172d7gOg4+s=';
const API_ENDPOINT = 'https://api.topstepx.com/api/Auth/loginKey';

export const authenticate = async () => {
  try {
    console.log("Attempting to authenticate with Topstep API...");
    
    const response = await fetch(API_ENDPOINT, {
      method: 'POST',
      headers: {
        'accept': 'text/plain',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        userName: 'quantsavvi',
        apiKey: API_KEY
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    
    if (data.success && data.errorCode === 0) {
      console.log('✅ Login successful! Session token received');
      setSessionToken(data.token);
      return data.token;
    } else {
      throw new Error(`API error: ${data.errorMessage || 'Unknown error'}`);
    }
  } catch (error) {
    console.error('❌ Authentication failed:', error);
    throw error;
  }
};

export { API_KEY, API_ENDPOINT };

// Auto-run authentication when script is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  authenticate().catch(console.error);
}