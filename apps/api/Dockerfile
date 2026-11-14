FROM python:3.12-slim
WORKDIR /app
COPY apps/api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY apps/api/app.py /app/app.py
COPY apps/api/auth.py /app/auth.py
COPY apps/api/experiences.py /app/experiences.py
COPY apps/api/coragem_routes.py /app/coragem_routes.py
COPY apps/api/coragem_engine.py /app/coragem_engine.py
COPY apps/web/catalogo.json /app/catalogo.json
COPY apps/web/experiencias.json /app/experiencias.json
ENV CATALOG_PATH=/app/catalogo.json
ENV EXPERIENCES_PATH=/app/experiencias.json
ENV NG_DB_PATH=/data/sandbox.sqlite3
EXPOSE 8090
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8090"]
