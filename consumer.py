from kafka import KafkaConsumer
import json
import psycopg2
import os

# 连接 PostgreSQL
conn = psycopg2.connect(
    dbname="mydatabase",
    user="myuser",
    password="mypassword",
    host="postgres",  # 关键：Docker 内的 PostgreSQL 服务名
    port="5432"
)
cursor = conn.cursor()

# 监听 Kafka 主题
consumer = KafkaConsumer(
    "orders",
    bootstrap_servers="kafka:9092",  # 关键：Kafka 运行在 Docker 里
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=False
)

print("Kafka Consumer 正在监听 `orders` 主题...")

for message in consumer:
    order = message.value
    print(f"Received: {order}")

    # 插入数据到 PostgreSQL
    cursor.execute("""
    INSERT INTO orders (user_id, product_id, quantity, price, timestamp)
    VALUES (%s, %s, %s, %s, %s);
""", (order["user_id"], order["product_id"], order["quantity"], order["price"], order["timestamp"]))


    conn.commit()