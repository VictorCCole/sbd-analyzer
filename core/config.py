# ========================================
# CONFIGURAÇÕES GERAIS DO PROJETO
# ========================================

# Squat (Agachamento)
ANGULO_MINIMO_PROFUNDIDADE_SQUAT = 100  # ângulo do joelho
TOLERANCIA_QUADRIL_SQUAT = 5
MIN_SUBIDA_OMBRO_SQUAT = 3
FRAMES_ANALISE_SQUAT = 15
ANGULO_MAXIMO_TRONCO = 50  # graus

# Deadlift (Levantamento Terra)
TOLERANCIA_QUADRIL_DEADLIFT = 5
MIN_SUBIDA_OMBRO_DEADLIFT = 3
FRAMES_ANALISE_DEADLIFT = 15

# Bench Press (Supino)
MARGEM_PEITO_BENCH = 10
ANGULO_MINIMO_EXTENSAO_BENCH = 165
FRAMES_ANALISE_BENCH = 20  # <- Novo: número de frames analisados para descida/subida
TOLERANCIA_MOVIMENTO_BENCH = 2  # <- Novo: tolerância mínima de mudança para considerar descida/subida

# Redimensionamento de Vídeo
MAX_WIDTH = 640
MAX_HEIGHT = 640