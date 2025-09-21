
let sessionToken = null;

export const setSessionToken = (token) => {
  sessionToken = token;
  console.log("Session token set:", token ? "✅ Token stored" : "❌ Token cleared");
};

export const getSessionToken = () => {
  return sessionToken;
};

export const clearSessionToken = () => {
  sessionToken = null;
  console.log("Session token cleared");
};

// Check if token is expired (assuming JWT format)
export const isTokenExpired = (token) => {
  if (!token) return true;
  
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Math.floor(Date.now() / 1000);
    return payload.exp < currentTime;
  } catch (error) {
    console.error('Error parsing token:', error);
    return true;
  }
};

export const getValidToken = () => {
  const token = getSessionToken();
  if (!token || isTokenExpired(token)) {
    console.log("No valid token available");
    return null;
  }
  return token;
};

console.log("Current session token:", getSessionToken() ? "Token exists: " + getSessionToken() : "No token");