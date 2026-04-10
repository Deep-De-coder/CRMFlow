FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

ENV SF_USERNAME=""
ENV SF_PASSWORD=""
ENV SF_SECURITY_TOKEN=""
ENV SF_DOMAIN="login"
ENV APP_ENV="production"
ENV LOG_LEVEL="INFO"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
