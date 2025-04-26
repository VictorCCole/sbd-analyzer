# SBD Analyzer – Analisador de Agachamento com Python e MediaPipe

Este projeto realiza a análise técnica de vídeos de agachamento usando visão computacional, com foco em detectar se o quadril passa a linha do joelho. É ideal para aplicações como avaliação de desempenho no Powerlifting e feedback postural.

---

## ✅ Requisitos

- **Python 3.10.11**
- **pip 23.2.1**
- **mediapipe 0.10.5** (versão estável com suporte à API `solutions.pose`)

---

## 🧰 Instalação

### 1. Crie e ative o ambiente virtual:

```bash
python -m venv .venv
# PowerShell
.venv\Scripts\Activate.ps1
# ou CMD
.venv\Scripts\activate.bat
```

### 2. Instale as dependências:

```bash
pip install opencv-python mediapipe==0.10.5
pip install fastapi uvicorn python-multipart
```

---

## ▶️ Como rodar

1. Coloque seu vídeo em `media/seu_video.mp4`
2. Execute o script principal:

```bash
python main.py
```

3. Controles durante a reprodução:
   - **Espaço**: Play/Pause
   - **R**: Reiniciar
   - **ESC**: Sair

---

## 🧠 O que o sistema faz atualmente

- Detecta os pontos do esqueleto com MediaPipe
- Verifica se o quadril (hip) está abaixo da linha do joelho (knee)
- Exibe feedback visual na tela ("OK" ou "Incompleto") por lado
- Funciona com vídeos verticais (gravados por celular)

---

## 📁 Estrutura do Projeto

```
sbd-analyzer/
├── main.py                      # Script principal
├── core/
│   ├── __init__.py
│   ├── squat.py                 # Lógica de análise do agachamento
│   └── utils.py                 # Funções auxiliares (cálculo, conversão)
├── media/
│   └── seu_video.mp4            # Vídeo de entrada
```

---

## 💡 Futuras implementações

- Detecção de inclinação excessiva do tronco
- Análise de valgismo do joelho
- Suporte a supino e levantamento terra
- API (FastAPI) para receber vídeo via interface web
- Integração com banco de dados para salvar histórico de análises

---

## 📌 Observações

- A versão mais recente do MediaPipe (0.10.21+) **não é compatível com a API antiga `mediapipe.solutions`**.  
  Por isso, utilizamos a versão `0.10.5` neste projeto.
