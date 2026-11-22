FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir psycopg2-binary barnum
COPY load_items.py .
CMD ["python", "load_items.py"]