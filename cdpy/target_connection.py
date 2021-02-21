import enum
import json
import logging
import queue
import threading
from collections import defaultdict
from typing import Any, Callable

import websocket

from .cdpy import EventParserError, Target, parse_event

logger = logging.getLogger(__name__)


class ConnectionStatus(enum.Enum):
    DISCONNECTED = 0
    CONNECTED = 1
    DEFAULT = DISCONNECTED


class TargetConnection:
    def __init__(self, target: Target):
        self.target = target

        self.status = ConnectionStatus.DEFAULT
        self._current_message_id = 0
        self._websocket = None

        # Threads
        self._event_thread = threading.Thread(target=self._event_loop)
        self._event_thread.daemon = True  # Stops when main stops
        self._receive_msg_thread = threading.Thread(target=self._receive_msg_loop)
        self._receive_msg_thread.daemon = True  # Stops when main stops
        self._threads_stopped = threading.Event()

        # Event handling
        self._event_queue = queue.Queue()
        self._event_handlers: defaultdict[
            str, list[Callable[[Any], None]]
        ] = defaultdict(list)

    def connect(self):
        # Start websocket connection
        self._websocket = websocket.create_connection(
            self.target.websocket_debugg_url, enable_multithread=True
        )

        # Start threads
        self._threads_stopped.clear()
        self._receive_msg_thread.start()
        self._event_thread.start()

        self.status == ConnectionStatus.CONNECTED

    def disconnect(self):
        # Stop threads
        self._threads_stopped.set()

        # Disconnect websocket
        if self._websocket:
            self._websocket.close()

        self.status == ConnectionStatus.DISCONNECTED

    def wait(self, timeout=None):
        """Block thread until the connection is closed.

        Parameters
        ----------
        timeout:
            Time in seconds after which to stop blocking
        """

        if self._threads_stopped:
            return

        if timeout:
            return self._threads_stopped.wait(timeout)
        else:
            self._receive_msg_thread.join()
            self._event_thread.join()

    def subscribe(self, event: str, event_handler: Callable[[Any], None]):
        self._event_handlers[event].append(event_handler)

    def unsubscribe(self, event: str, event_handler: Callable):
        self._event_handlers[event].remove(event_handler)

    def _send(self, message: dict):
        # Ensure message has id
        if not "id" in message:
            self._current_message_id += 1
            message["id"] = self._current_message_id

        message_str = json.dumps(message)

    def _receive_msg_loop(self):
        """Receive and handle messages from websocket connection."""

        while not self._threads_stopped.is_set():
            try:
                self._websocket.settimeout(1)
                msg_json = json.loads(self._websocket.recv())
            except websocket.WebSocketTimeoutException:
                return
            except (websocket.WebSocketException, OSError):
                if not self._threads_stopped.is_set():
                    logger.error(
                        "Error trying to receive message from websocket", exc_info=True
                    )
                    self._threads_stopped.clear()
                return

            if "method" in msg_json:
                # Pass event to event queue. There it will be handled by the event thread.
                # This way the connection is not throttled by event handlers.
                self._event_queue.put(msg_json)
            elif "id" in msg_json:
                pass  # TODO handle method messages
            else:
                logger.warn(f"Unknown message: {msg_json}")

    def _event_loop(self):
        while not self._threads_stopped.is_set():
            # Try getting the next event
            try:
                event_json = self._event_queue.get(timeout=1)
            except queue.Empty:
                continue

            # Call handlers with event
            method = event_json["method"]
            if method in self._event_handlers:
                try:
                    event = parse_event(event_json)
                    for handler in self._event_handlers[method]:
                        handler(event)
                except EventParserError:
                    logger.error(f"Couldn't parse event: {event_json}")
                except Exception:
                    logger.error(f"Error while executing handler for event: {event}")

            # Indicates that the process on the previous queue.get is done
            self._event_queue.task_done()
