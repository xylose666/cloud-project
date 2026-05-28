from flask import Flask, jsonify
import redis
import os

app = Flask(__name__)

# 连接 Redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD", None),
    decode_responses=True
)

@app.route("/api/data")
def get_data():
    # 每次访问接口，Redis 的 count 增加 1
    count = redis_client.incr("page_views")
    return jsonify({
        "status": "success",
        "message": "通信正常！这是后端返回的数据",
        "views": count
    })

@app.route("/")
def home():
    return "Backend Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)