import { HubConnectionBuilder, HttpTransportType } from '@microsoft/signalr';
import { EventEmitter } from 'events';

// Create an event emitter to handle SignalR events
const signalrEvents = new EventEmitter();

let connection = null;

export const setupSignalRConnection = async (token, contractId) => {
    try {
        const JWT_TOKEN = token;
        const marketHubUrl = 'https://rtc.topstepx.com/hubs/market?access_token=' + JWT_TOKEN;
        const CONTRACT_ID = contractId;

        // Create the SignalR connection
        connection = new HubConnectionBuilder()
            .withUrl(marketHubUrl, {
                skipNegotiation: true,
                transport: HttpTransportType.WebSockets,
                accessTokenFactory: () => JWT_TOKEN,
                timeout: 10000
            })
            .withAutomaticReconnect()
            .build();

        // Handle connection events
        connection.onreconnecting((error) => {
            console.log("SignalR connection lost due to error:", error);
        });

        connection.onreconnected((connectionId) => {
            console.log("SignalR connection reestablished. Connected with connectionId:", connectionId);
            // Resubscribe after reconnection
            subscribe();
        });

        connection.onclose((error) => {
            console.log("SignalR connection closed due to error:", error);
        });

        // Set up event handlers for different data types
        connection.on('GatewayQuote', (contractId, data) => {
            signalrEvents.emit("quote", { contractId, data });
        });

        connection.on('GatewayTrade', (contractId, data) => {
            signalrEvents.emit("trade", { contractId, data });
        });

        connection.on('GatewayDepth', (contractId, data) => {
            signalrEvents.emit("depth", { contractId, data });
        });

        // Subscribe and unsubscribe functions
        const subscribe = () => {
            connection.invoke('SubscribeContractQuotes', CONTRACT_ID);
            connection.invoke('SubscribeContractTrades', CONTRACT_ID);
            connection.invoke('SubscribeContractMarketDepth', CONTRACT_ID);
            console.log(`Subscribed to ${CONTRACT_ID} market data`);
        };

        const unsubscribe = () => {
            connection.invoke('UnsubscribeContractQuotes', CONTRACT_ID);
            connection.invoke('UnsubscribeContractTrades', CONTRACT_ID);
            connection.invoke('UnsubscribeContractMarketDepth', CONTRACT_ID);
            console.log(`Unsubscribed from ${CONTRACT_ID} market data`);
        };

        // Start the connection
        await connection.start();
        console.log("SignalR connection started successfully");

        // Subscribe to the contract
        subscribe();

        return { connection, subscribe, unsubscribe };
    } catch (error) {
        console.error("Error setting up SignalR connection:", error);
        throw error;
    }
};

export const closeConnection = async () => {
    if (connection) {
        await connection.stop();
        console.log("SignalR connection closed");
    }
};

export { signalrEvents };