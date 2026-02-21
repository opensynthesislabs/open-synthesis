FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ../src/open_synthesis/handler.py .
COPY ../prompts/ ./prompts/

CMD ["python", "-u", "handler.py"]
