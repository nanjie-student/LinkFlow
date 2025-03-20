from flask import Flask, jsonify
from kafka import KafkaProducer
import random
import os
import time
import json
import threading

app = Flask(__name__)

# 连接 Kafka（优化参数）
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")  # 让 Kafka 连接到 Docker 容器名
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    retries=5,
    acks='all'  # 确保 Kafka 成功接收数据
)

# 生成模拟订单数据
def generate_order():
    return {
        "order_id": random.randint(1000, 9999),
        "user_id": random.randint(1, 500),
        "product_id": random.randint(1, 100),
        "quantity": random.randint(1, 5),
        "price": round(random.uniform(10, 500), 2),
        "timestamp": time.time()
    }

@app.route("/order", methods=["GET"])
def get_order():
    """仅用于测试：生成一个订单并返回"""
    order = generate_order()
    return jsonify(order), 200

@app.route("/send_order", methods=["POST"])
def send_order():
    """手动发送订单到 Kafka"""
    order = generate_order()
    producer.send("orders", value=order)
    producer.flush()  # 确保立即发送
    return jsonify(order), 200

# 让 Flask **每 5 秒** 自动生成订单数据并发送到 Kafka
def send_order_periodically():
    while True:
        order = generate_order()
        try:
            producer.send("orders", value=order)
            producer.flush()  # 立即发送数据
            print(f"Sent: {order}")
        except Exception as e:
            print(f"Error sending order to Kafka: {e}")
        time.sleep(5)  # **测试时改为 5 秒，生产环境可以调整**

# 启动后台线程，不会阻塞 Flask API
threading.Thread(target=send_order_periodically, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True, port=5000)