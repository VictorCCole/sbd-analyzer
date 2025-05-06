import cv2
import math

def ponto_em_pixels(landmark, largura, altura):
    """Converte ponto normalizado em coordenadas de pixel."""
    return int(landmark.x * largura), int(landmark.y * altura)

def redimensionar(frame, max_width=640, max_height=640):
    h, w = frame.shape[:2]
    aspect_ratio = w / h
    if w > h:
        new_width = max_width
        new_height = int(max_width / aspect_ratio)
    else:
        new_height = max_height
        new_width = int(max_height * aspect_ratio)

    resized = cv2.resize(frame, (new_width, new_height))
    canvas = cv2.copyMakeBorder(
        resized,
        top=(max_height - new_height) // 2,
        bottom=(max_height - new_height) // 2,
        left=(max_width - new_width) // 2,
        right=(max_width - new_width) // 2,
        borderType=cv2.BORDER_CONSTANT,
        value=(0, 0, 0)
    )
    return canvas

def load_video(path):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise ValueError(f"Erro ao abrir o vídeo: {path}")
    return cap

def calcular_angulo(a, b, c):
    """Calcula o ângulo entre três pontos (em pixels)."""
    angulo = math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0]) -
        math.atan2(a[1] - b[1], a[0] - b[0])
    )
    angulo = abs(angulo)
    if angulo > 180:
        angulo = 360 - angulo
    return angulo
