import os
import redis
import threading
from flask import Flask, request, jsonify, send_from_directory
from urllib.parse import unquote

app = Flask(__name__)

# Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

# Redis keys
MALWARE_KEY = "malware:urls"

# ============================================
# PUB/SUB - Real-time updates across all instances
# ============================================

def listen_for_updates():
    """Background thread that listens for new malware URLs"""
    pubsub = redis_client.pubsub()
    pubsub.subscribe('malware-updates')
    print("🔔 Listening for real-time malware updates...")
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            url = message['data']
            redis_client.sadd(MALWARE_KEY, url)
            print(f"🔄 Real-time update: {url} added to blocked list")

threading.Thread(target=listen_for_updates, daemon=True).start()

# ============================================
# MAIN API - Check if URL is safe
# ============================================

@app.route('/urlinfo/1/<path:url_path>', methods=['GET'])
def check_url(url_path):
    url = unquote(url_path)
    
    if not url or len(url) > 2048:
        return jsonify({"error": "Invalid URL"}), 400
    
    is_malicious = redis_client.sismember(MALWARE_KEY, url)
    
    return jsonify({
        "url": url,
        "safe": not is_malicious
    }), 200

# ============================================
# ADMIN - Add URLs (publishes to all instances)
# ============================================

@app.route('/admin/add', methods=['POST'])
def add_url():
    data = request.get_json()
    url = data.get('url', '')
    
    if not url:
        return jsonify({"error": "missing url"}), 400
    
    redis_client.sadd(MALWARE_KEY, url)
    
    redis_client.publish('malware-updates', url)
    
    print(f"📢 Published update: {url}")
    return jsonify({"status": "added", "url": url}), 201

@app.route('/admin/remove', methods=['POST'])
def remove_url():
    data = request.get_json()
    url = data.get('url', '')
    
    if url:
        redis_client.srem(MALWARE_KEY, url)
        return jsonify({"status": "removed", "url": url}), 200
    return jsonify({"error": "missing url"}), 400

@app.route('/admin/list', methods=['GET'])
def list_urls():
    urls = list(redis_client.smembers(MALWARE_KEY))
    return jsonify({"blocked_urls": urls, "total": len(urls)}), 200

# ============================================
# Web Interface & Health
# ============================================

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

# ============================================
# Run the app
# ============================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    print(f" URL Lookup Service running on port {port}")
    print(" Redis Pub/Sub enabled - real-time updates across all instances")
    app.run(host='0.0.0.0', port=port, debug=False)