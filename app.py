from flask import Flask, request, jsonify # type: ignore
import requests # type: ignore
from threading import Lock
import time

app = Flask(__name__)
WINDOW_SIZE = 10

lock = Lock()

window = []

URLS = {
    'p': 'http://20.244.56.144/test/primes',
    'f': 'http://20.244.56.144/test/fibo',
    'e': 'http://20.244.56.144/test/even',
    'r': 'http://20.244.56.144/test/rand'
}

def fetch_numbers(url):
    try:
        response = requests.get(url, timeout=0.5)
        response.raise_for_status()
        return response.json().get('numbers', [])
    except (requests.RequestException, ValueError):
        return []

@app.route('/numbers/<id>', methods=['GET'])
def get_numbers(id):
    if id not in URLS:
        return jsonify({"error": "Invalid ID"}), 400

    url = URLS[id]

    with lock:
        window_prev_state = list(window)
        
        new_numbers = fetch_numbers(url)
        for num in new_numbers:
            if num not in window:
                if len(window) >= WINDOW_SIZE:
                    window.pop(0)  
                window.append(num)
        
        window_curr_state = list(window)
        if window_curr_state:
            avg = sum(window_curr_state) / len(window_curr_state)
        else:
            avg = 0

    response = {
        "windowPrevState": window_prev_state,
        "windowCurrState": window_curr_state,
        "numbers": new_numbers,
        "avg": round(avg, 2)
    }
    
    return jsonify(response)

if __name__ == '_main_':
    app.run(debug=True)