FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY client/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY client/ffmpeg_remote.py /app/ffmpeg_remote.py

ENTRYPOINT ["python", "/app/ffmpeg_remote.py"]
CMD ["--help"]
