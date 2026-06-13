import datetime
import json
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

app = Flask(__name__)
CORS(app)

FOLDER = "dispositivos"
if not os.path.exists(FOLDER):
    os.makedirs(FOLDER)

def generate_self_signed_cert():
    if not os.path.exists("cert.pem"):
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, u"localhost")])
        cert = x509.CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(
            key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(
            datetime.datetime.utcnow()).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)).sign(key, hashes.SHA256(), default_backend())
        with open("cert.pem", "wb") as f: f.write(cert.public_bytes(serialization.Encoding.PEM))
        with open("key.pem", "wb") as f: f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()))
    return ("cert.pem", "key.pem")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update_location', methods=['POST'])
def update_location():
    data = request.json
    if data:
        device_id = request.remote_addr.replace(".", "_")
        payload = {
            "id": device_id,
            "lat": data.get("latitude"),
            "lon": data.get("longitude"),
            "dir": data.get("direcao") if data.get("direcao") is not None else 0.0,
            "time": datetime.datetime.now().strftime("%H:%M:%S")
        }
        with open(os.path.join(FOLDER, f"{device_id}.json"), "w") as f:
            json.dump(payload, f)
        return jsonify({"status": "success", "device": device_id})
    return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    ssl_files = generate_self_signed_cert()
    app.run(host='0.0.0.0', port=5000, ssl_context=ssl_files, debug=False)