# TopStepX Real-Time Market Data Pipeline

This repository provides a complete real-time trading data pipeline for TopStep's NASDAQ futures market, integrating Node.js, Python, and SignalR technologies. It enables authentication, session management, real-time market data streaming, and machine learning-based training & prediction.
## Features
- **Session Management**: Robust JWT authentication, token validation, and refresh logic for TopStep API.
- **SignalR Client**: Real-time WebSocket connection to TopStep's market data hub using @microsoft/signalr.
- **Market Data Streaming**: Subscribes to and processes live quote, trade, and market depth data for NASDAQ futures (`/NQ`).
- **Modular Codebase**: Clean ES module structure for Node.js, with clear separation of concerns (sessions, SignalR, server, test).

## Project Structure

- `server.js` — Main Node.js server integrating session management and SignalR market data streaming.
- `signalRClient.js` — SignalR connection wrapper with event emitters for quote, trade, and depth data.
- `sessions/` — Session management system (authentication, token management, validation).
- `test.js` — Standalone test for SignalR connection and token management.
- `requirements.txt` — Python dependencies for ML and WebSocket relay.
- `myenv/` — Python virtual environment (do not edit directly).

## Setup & Usage

### 1. Python Environment

```sh
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
```

### 2. Node.js Environment

Install Node.js (v22+) and NPM. Then:

```sh
npm install
```

### 3. Running the Server

```sh
node server.js
```
This will authenticate with TopStep, connect to the SignalR market data hub, and stream real-time data.

### 4. Python WebSocket Relay

```sh
python websocketRelay.py
```
This will start the Python server for ML-based prediction and data relay.

## Key Technologies

- Node.js (ES modules)
- @microsoft/signalr
- Python 3.12+
- pandas, numpy, scikit-learn, matplotlib, websockets

## Example Output

```
✅ Login successful! Session token received
SignalR connection started successfully
🚀 SignalR connection established and subscribed to market data
📊 Quote Update for CON.F.US.ENQ.U25: {...}
💰 Trade Update for CON.F.US.ENQ.U25: [...]
📈 Market Depth for CON.F.US.ENQ.U25: [...]
```

## License

MIT License
