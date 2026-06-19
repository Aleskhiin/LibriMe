FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

ENV TTS_HOME=/app/.local/share/tts
ENV XDG_DATA_HOME=/app/.local/share
ENV PHONEMIZER_ESPEAK_LIBRARY=/usr/lib/x86_64-linux-gnu/libespeak-ng.so.1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    libsndfile1 \
    libgl1 \
    libglib2.0-0 \
    libreoffice \
    espeak-ng \
    libespeak-ng1 \
    ffmpeg \
    git \
    curl \
    locales \
    && sed -i 's/# *de_AT.UTF-8 UTF-8/de_AT.UTF-8 UTF-8/' /etc/locale.gen \
    && sed -i 's/# *de_DE.UTF-8 UTF-8/de_DE.UTF-8 UTF-8/' /etc/locale.gen \
    && sed -i 's/# *en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=de_AT.UTF-8
ENV LANGUAGE=de_AT:de:en
ENV LC_ALL=de_AT.UTF-8

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/.local/share/tts

RUN python -c "from TTS.api import TTS; \
models=['tts_models/de/thorsten/tacotron2-DDC','tts_models/en/ljspeech/tacotron2-DDC']; \
[ TTS(model_name=m, progress_bar=False, gpu=False).tts_to_file(text='Test', file_path='/tmp/test_' + str(i) + '.wav') for i, m in enumerate(models) ]"

COPY . .

ARG UID=10001
RUN adduser --disabled-password --gecos "" --uid "${UID}" appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]