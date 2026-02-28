import json
import logging
import threading
import time
import websocket

logger = logging.getLogger(__name__)

class TracParser:
    def __init__(self, rpc_url, on_event_callback):
        self.rpc_url = rpc_url
        self.on_event_callback = on_event_callback
        self.ws = None
        self.should_run = True

    def _on_message(self, ws, message):
        try:
            data = json.loads(message)
            # Normalize event data. Adjust based on actual Trac RPC payload structure
            event = {
                "type": data.get("type", "unknown"),
                "token": data.get("token", ""),
                "amount": float(data.get("amount", 0.0)),
                "wallet": data.get("wallet", ""),
                "timestamp": data.get("timestamp", int(time.time()))
            }
            
            self.on_event_callback(event)
        except Exception as e:
            logger.error(f"Error parsing message: {e}")

    def _on_error(self, ws, error):
        logger.error(f"WebSocket Error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        logger.info("WebSocket connection closed")

    def _on_open(self, ws):
        logger.info("WebSocket connection opened to Trac RPC")
        # Example subscribe payload
        subscribe_msg = {
            "action": "subscribe",
            "contracts": ["all"]
        }
        ws.send(json.dumps(subscribe_msg))

    def run_forever(self):
        while self.should_run:
            try:
                if not self.rpc_url:
                    logger.warning("No TRAC_RPC_URL provided. Parser waiting...")
                    time.sleep(10)
                    continue

                self.ws = websocket.WebSocketApp(
                    self.rpc_url,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close,
                    on_open=self._on_open
                )
                self.ws.run_forever()
            except Exception as e:
                logger.error(f"WebSocket runner exception: {e}")
            
            if self.should_run:
                logger.info("Reconnecting in 5 seconds...")
                time.sleep(5)
                
    def start(self):
        self.thread = threading.Thread(target=self.run_forever, daemon=True)
        self.thread.start()

    def stop(self):
        self.should_run = False
        if self.ws:
            self.ws.close()
