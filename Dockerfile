# Gunakan Python 3.11, bukan 3.13
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Salin semua file ke container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Jalankan app pakai sitecustomize patch
CMD ["python", "-m", "sitecustomize", "main.py"]
