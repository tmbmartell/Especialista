FROM python:3.12-slim
WORKDIR /app
COPY apps/api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY apps/api/app.py /app/app.py
COPY apps/web/catalogo.json /app/catalogo.json
ENV CATALOG_PATH=/app/catalogo.json
EXPOSE 8090
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8090"]
