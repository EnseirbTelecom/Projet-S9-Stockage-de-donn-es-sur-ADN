FROM python:3.12-slim

WORKDIR /app

# Installation des dépendances
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Port de FastAPI
EXPOSE 8000

# Démarrage de l'API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]