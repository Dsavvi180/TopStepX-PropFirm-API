## TradingView-TopStep-Bridge

This bridge connects TradingView trading strategies to the TopStep prop-firm API for live trade execution.

When a TradingView strategy generates a signal, it sends a webhook alert to this bridge, which receives, verifies, and forwards the trade to the TopStep API for execution. Each executed trade — along with its success status — triggers a Discord alert for real-time monitoring.

The bridge broadcasts trade execution across multiple TopStep accounts simultaneously, and is designed to extend easily to other prop-firm APIs. Session management runs continuously in the background, with API keys revalidated at regular intervals to ensure uninterrupted access to the TopStep API.

This bridging server runs on a home-made Raspberry Pi server.
