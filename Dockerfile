FROM python:3.12-alpine

# Configurações recomendadas para Python em containers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala cron e dependências básicas
RUN apk update && apk add --no-cache \
    tzdata \
    bash \
    busybox-suid \
    && rm -rf /var/cache/apk/*

# Diretório da aplicação
WORKDIR /app

# Copia arquivos
COPY requirements.txt .
COPY rsi_screening.py .
COPY lib/ ./lib/
COPY crontab /etc/crontabs/root

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Ajusta permissões do cron
RUN chmod 0644 /etc/crontabs/root

# Arquivo de log do cron
RUN touch /var/log/cron.log

# Inicia cron em primeiro plano
CMD ["crond", "-f", "-l", "2"]