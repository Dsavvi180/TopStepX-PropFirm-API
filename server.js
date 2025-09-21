// server.js

import { setupSignalRConnection, signalrEvents } from "./signalRClient.js";
import { sessionManager } from "./sessions/index.js";
  const CRUDE_OIL = 'CON.F.US.NQM.Q25'
  const NATURAL_GAS = 'CON.F.US.NQG.Q25'
  const MICRO_NQ = 'CON.F.US.MNQ.U25'
  const EMINI_NQ = 'CON.F.US.ENQ.U25'
// Contract ID to subscribe to
const contractId = "CON.F.US.NQM.Q25"; //NQ

// Initialize the connection with session management
const initializeSignalRConnection = async () => {
    try {
        // Get a valid JWT token from session manager
        const authToken = await sessionManager.getValidToken();
        console.log('✅ Got valid JWT token from session manager');
        
        // Setup SignalR connection
        await setupSignalRConnection(authToken, contractId);
        
        console.log('🚀 SignalR connection established and subscribed to market data');
    } catch (error) {
        console.error('❌ Failed to initialize SignalR connection:', error);
        throw error;
    }
};

// Event handlers for market data
signalrEvents.on("quote", ({ contractId, data }) => {
    console.log(`📊 Quote Update for ${contractId}:`, data);
    // Process quote data (bid/ask/last prices)
});

signalrEvents.on("trade", ({ contractId, data }) => {
    console.log(`💰 Trade Update for ${contractId}:`, data);
    // Process trade data (executed trades)
});

signalrEvents.on("depth", ({ contractId, data }) => {
    console.log(`📈 Market Depth for ${contractId}:`, data);
    // Process order book data
});

// Start the connection
initializeSignalRConnection().catch(console.error);

// Graceful shutdown
process.on('SIGINT', async () => {
    console.log('Shutting down gracefully...');
    process.exit(0);
});
