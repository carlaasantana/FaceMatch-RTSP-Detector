from flask import Flask, render_template, send_from_directory
import os
import json
import glob
from collections import defaultdict

app = Flask(__name__)
EVENTOS_DIR = "eventos_detectados"

@app.route('/')
def index():
    eventos = defaultdict(list)
    json_files = glob.glob(os.path.join(EVENTOS_DIR, "*.json"))

    for file in sorted(json_files, reverse=True):
        try:
            with open(file) as f:
                data = json.load(f)
                camera = data.get("camera", "Desconhecida")
                eventos[camera].append(data)
        except json.JSONDecodeError:
            print(f"Erro ao decodificar o arquivo {file}")
    
    return render_template("dashboard.html", eventos=eventos)

@app.route('/imagem/<nome>')
def imagem(nome):
    return send_from_directory(EVENTOS_DIR, nome)

if __name__ == "__main__":
    app.run(debug=True, port=8080)