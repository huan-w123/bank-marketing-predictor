FROM python:3.11-slim

WORKDIR /app

ARG PIP_INDEX_URL=https://pypi.org/simple

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 120 -i "${PIP_INDEX_URL}" -r requirements.txt

COPY app.py .
COPY src/ ./src/
COPY models/ ./models/

EXPOSE 8004

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -fsS http://localhost:8004/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=8004", "--server.address=0.0.0.0"]
