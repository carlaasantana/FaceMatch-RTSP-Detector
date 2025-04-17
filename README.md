# FaceMatch-RTSP-Detector

## Descrição
Este projeto implementa um sistema de reconhecimento facial em tempo real utilizando a biblioteca InsightFace. O sistema monitora múltiplas câmeras RTSP, detecta rostos nos frames capturados e os compara com uma base de rostos conhecidos. Quando um rosto é reconhecido, o sistema registra o evento salvando uma imagem e um arquivo JSON com os detalhes.

## Funcionalidades
- **Detecção de Rostos**: Utiliza o modelo `buffalo_l` do InsightFace para detectar rostos em frames de vídeo.
- **Reconhecimento Facial**: Compara os rostos detectados com uma base de rostos conhecidos usando embeddings.
- **Registro de Novos Rostos**: Permite registrar novos rostos pressionando a tecla 'r' durante a execução.
- **Monitoramento Multi-câmera**: Suporte para monitorar múltiplas câmeras simultaneamente via threads.
- **Registro de Eventos**: Salva imagens e metadados (JSON) de eventos de reconhecimento.

## Pré-requisitos
- Python 3.x
- Bibliotecas:
  - `opencv-python` (cv2)
  - `insightface`
  - `numpy`

## Instalação
1. Clone o repositório:
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd <DIRETORIO_DO_PROJETO>
