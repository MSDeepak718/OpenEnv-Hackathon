FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir \
    "fastapi>=0.115.0" \
    "uvicorn[standard]>=0.34.0" \
    "openai>=1.0.0" \
    "pydantic>=2.0.0" \
    "python-dotenv>=1.0.0" \
    "openenv>=0.1.13"

EXPOSE 7860

CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "7860"]