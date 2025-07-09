from flask import Flask, request, jsonify
from app import app, db
from models import User, Carte, Transaction

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run()
