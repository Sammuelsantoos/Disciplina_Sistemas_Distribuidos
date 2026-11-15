import json
import socket
import threading
import time
import unittest

from src.server.main_server import run_server
from src.server.services.event_broker import EventBroker


class EventBrokerTests(unittest.TestCase):
    def test_publish_sends_event_to_subscribers(self):
        broker = EventBroker()
        received = []

        class DummySubscriber:
            def __init__(self, container):
                self.container = container

            def receive(self, message):
                self.container.append(message)

        subscriber = DummySubscriber(received)
        broker.subscribe("match.events", subscriber)
        broker.publish("match.events", {"event_type": "gol", "team": "Flamengo"})

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]["topic"], "match.events")

    def test_server_keeps_subscriber_connection_open_for_notifications(self):
        port = 65001
        thread = threading.Thread(
            target=run_server,
            kwargs={"host": "127.0.0.1", "port": port},
            daemon=True,
        )
        thread.start()
        time.sleep(0.3)

        subscriber = socket.create_connection(("127.0.0.1", port), timeout=2)
        subscriber.sendall(
            json.dumps({"action": "SUBSCRIBE", "topic": "match.events", "subscriber_id": "viewer"}).encode("utf-8")
        )
        ack = subscriber.recv(4096).decode("utf-8")
        self.assertIn('"status": "SUBSCRIBED"', ack)

        publisher = socket.create_connection(("127.0.0.1", port), timeout=2)
        publisher.sendall(
            json.dumps(
                {
                    "action": "PUBLISH",
                    "topic": "match.events",
                    "payload": {"event_type": "gol", "team": "Flamengo", "player": "Pedro", "minute": "13'"},
                }
            ).encode("utf-8")
        )
        publisher_response = publisher.recv(4096).decode("utf-8")
        self.assertIn('"status": "PUBLISHED"', publisher_response)

        notification = subscriber.recv(4096).decode("utf-8")
        self.assertIn('"action": "NOTIFY"', notification)

        subscriber.close()
        publisher.close()


if __name__ == "__main__":
    unittest.main()
