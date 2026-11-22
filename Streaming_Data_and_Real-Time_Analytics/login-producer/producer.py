from kafka import KafkaProducer
import json
from datetime import datetime
import time
import random

# ⚠️ kafka:29092 = port interne (pas 9092 qui est l'externe)
producer = KafkaProducer(
    bootstrap_servers='kafka:29092',
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

devices = ['iPhone 15', 'Samsung Galaxy', 'MacBook Pro', 'Windows Laptop']
ips     = ['192.168.1.100', '203.0.113.22', '10.0.0.99']
platforms = ['ios', 'android', 'web']

print("🚀 Starting login-event producer (every 2s)...")

while True:
    event = {
        "user_id":    f"user_{random.randint(1,5)}",
        "timestamp":  datetime.utcnow().isoformat() + "Z",
        "ip":         random.choice(ips),
        "device":     random.choice(devices),
        "platform":   random.choice(platforms),
        "user_agent": "Mozilla/5.0",
    }
    producer.send('login-events', value=event)
    producer.flush()
    print(f"Sent: {event}")
    time.sleep(2)