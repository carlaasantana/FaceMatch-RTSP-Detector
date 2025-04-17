import cv2
import os
import json
import datetime
import threading
import numpy as np
from insightface.app import FaceAnalysis
from insightface.model_zoo import model_zoo
from numpy.linalg import norm

# inicializa o detector e extrator de embeddings
print("[INFO] Carregando modelos do InsightFace...")
detector = FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
detector.prepare(ctx_id=0)

# diretórios
PASTA_CONHECIDOS = "conhecidos"
PASTA_EVENTOS = "eventos_detectados"
os.makedirs(PASTA_EVENTOS, exist_ok=True)
os.makedirs(PASTA_CONHECIDOS, exist_ok=True)  # ertifique-se que a pasta de conhecidos exista

# configuração das câmeras
CAMERAS = {
    #aqui voce adiciona o link rstp da sua câmera
}

# threshold para considerar que é a mesma pessoa
THRESHOLD = 0.5

# carrega os rostos conhecidos (embedding + nome)
def carregar_conhecidos():
    conhecidos = {}
    for nome_arquivo in os.listdir(PASTA_CONHECIDOS):
        caminho = os.path.join(PASTA_CONHECIDOS, nome_arquivo)
        img = cv2.imread(caminho)
        faces = detector.get(img)
        if faces:
            face = faces[0]
            conhecidos[nome_arquivo.split(".")[0]] = face.embedding
            print(f"[INFO] Registrado: {nome_arquivo.split('.')[0]}")
    return conhecidos

conhecidos = carregar_conhecidos()

# função para calcular a similaridade entre embeddings
def comparar_embeddings(embedding1, embedding2):
    return norm(embedding1 - embedding2)

# Função para registrar um novo rosto
def registrar_rosto(nome_pessoa, frame):
    faces = detector.get(frame)
    if faces:
        face = faces[0]
        # Salva o rosto detectado na pasta de conhecidos
        caminho_imagem = os.path.join(PASTA_CONHECIDOS, f"{nome_pessoa}.jpg")
        cv2.imwrite(caminho_imagem, frame)
        
        # Salva o embedding do rosto
        conhecidos[nome_pessoa] = face.embedding
        print(f"[INFO] Novo rosto registrado: {nome_pessoa}")

# monitorar uma câmera com reconhecimento
def monitorar_camera(nome_camera, url_stream):
    cap = cv2.VideoCapture(url_stream)

    if not cap.isOpened():
        print(f"[ERRO] Não foi possível abrir a câmera {nome_camera}")
        return

    print(f"[INFO] Monitorando câmera: {nome_camera}")

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"[ERRO] Falha no stream da câmera {nome_camera}")
            break

        # detecta rostos no frame
        faces = detector.get(frame)

        reconhecidos = []

        for face in faces:
            box = face.bbox.astype(int)
            nome_identificado = "Desconhecido"

            # compara com todos os conhecidos
            for nome, embedding_registrado in conhecidos.items():
                dist = comparar_embeddings(face.embedding, embedding_registrado)
                if dist < THRESHOLD:
                    nome_identificado = nome
                    reconhecidos.append(nome)
                    break  # Para no primeiro match

            # desenha caixa e nome
            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
            cv2.putText(frame, nome_identificado, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Se alguém foi reconhecido, salva evento
        if reconhecidos:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_base = f"{nome_camera}_{timestamp}"
            img_path = os.path.join(PASTA_EVENTOS, f"{nome_base}.jpg")
            json_path = os.path.join(PASTA_EVENTOS, f"{nome_base}.json")

            cv2.imwrite(img_path, frame)
            with open(json_path, "w") as f:
                json.dump({
                    "camera": nome_camera,
                    "timestamp": timestamp,
                    "pessoas_reconhecidas": reconhecidos,
                    "imagem": img_path
                }, f, indent=2)

            print(f"[ALERTA] Reconhecido(s): {', '.join(reconhecidos)} na {nome_camera}")

        # Se pressionado 'r', registra um novo rosto
        if cv2.waitKey(1) & 0xFF == ord('r'):
            nome_pessoa = input("Digite o nome da pessoa para registrar: ")
            registrar_rosto(nome_pessoa, frame)

        cv2.imwrite(f"{nome_camera}_frame.jpg", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyWindow(f"{nome_camera}")

# inicia uma thread por câmera
for nome, url in CAMERAS.items():
    thread = threading.Thread(target=monitorar_camera, args=(nome, url))
    thread.start()
