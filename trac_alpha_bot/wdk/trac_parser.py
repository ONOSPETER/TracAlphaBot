import json
import logging
import threading
import time
import requests

logger = logging.getLogger(__name__)

class TracParser:
    def __init__(self, rpc_url, on_event_callback):
        # Fallback to a default public endpoint if TRAC_RPC_URL is not set or is a placeholder
        if not rpc_url or rpc_url.startswith("wss://"):
            # Using the explorer's standard API as a baseline for polling
            self.rpc_url = "https://explorer.trac.network/api/transactions"
        else:
            self.rpc_url = rpc_url
            
        self.on_event_callback = on_event_callback
        self.should_run = True
        self.last_processed_id = None

    def fetch_latest_events(self):
        try:
            # Poll the REST API for recent data
            # Adjust the endpoint/params depending on actual Trac API specs
            response = requests.get(self.rpc_url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Process the data into normalized events
            # This logic mimics processing generic transaction lists
            # from the explorer endpoint
            events_list = data.get("transactions", []) if isinstance(data, dict) else data
            
            # Ensure it is iterable
            if not isinstance(events_list, list):
                events_list = [events_list]

            for item in events_list:
                tx_id = item.get("txid", "") or item.get("id", "")
                
                # Simple duplicate prevention logic
                if tx_id and tx_id == self.last_processed_id:
                    continue
                
                if tx_id:
                    self.last_processed_id = tx_id
                
                # Normalize event
                event = {
                    "type": item.get("type", "transfer"),
                    "token": item.get("tick", "trac"),  # 'tick' often used in Tap/Ordinals
                    "amount": float(item.get("amt", item.get("amount", 0.0))),
                    "wallet": item.get("to_address", item.get("address", "")),
                    "timestamp": item.get("time", int(time.time()))
                }
                
                self.on_event_callback(event)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP Request error fetching Trac data: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON response from Trac API: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in Trac parser: {e}")

    def run_forever(self):
        logger.info(f"Starting Trac REST API polling parser using endpoint: {self.rpc_url}")
        while self.should_run:
            self.fetch_latest_events()
            
            # Wait before polling again to respect rate limits
            for _ in range(10): # 10 seconds polling interval, check should_run every second
                if not self.should_run:
                    break
                time.sleep(1)
                
    def start(self):
        self.thread = threading.Thread(target=self.run_forever, daemon=True)
        self.thread.start()

    def stop(self):
        self.should_run = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=2)
