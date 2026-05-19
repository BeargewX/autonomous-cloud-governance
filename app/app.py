from flask import Flask, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = '/app/data.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS incidents
                    (id INTEGER PRIMARY KEY, message TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return jsonify({
        'status': 'healthy',
        'service': 'Autonomous Cloud Governance',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/metrics')
def metrics():
    return jsonify({
        'cpu_usage': 'monitored',
        'memory_usage': 'monitored',
        'auto_healing': 'enabled',
        'finops': 'enabled'
    })

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)