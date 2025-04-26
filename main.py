from core.utils import load_video
from core import squat, deadlift, bench  # Agora importa também o bench

# Escolha o movimento
#movimento = "squat"
#movimento = "bench"
movimento = "deadlift"

video_path = "media/nat/nat_sumo.mp4"
cap = load_video(video_path)

if movimento == "squat":
    squat.analisar_squat(cap)
elif movimento == "deadlift":
    deadlift.analisar_deadlift(cap)
elif movimento == "bench":
    bench.analisar_bench(cap)
else:
    print("❌ Movimento não reconhecido.")
