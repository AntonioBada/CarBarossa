# Immagine base con Python 3.10
FROM python:3.10-slim

# Imposta la directory di lavoro nel container
WORKDIR /app

# Copia i requisiti e installa le dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il contenuto del progetto
COPY . .

# Espone la porta 5000 (o quella usata in server_clean.py)
EXPOSE 80

# Comando per avviare l'app
CMD ["python", "server_clean.py"]
