# Debian, not Alpine: the embedding runtime has no musl build. The model is downloaded at build time because the
# job has no internet access in the cluster (only M5 has).
FROM python:3.12-slim@sha256:5b5fe805d367f8f5a359ded6ab2652b7f9a206453ee6ee789c0045ba6ec15016 AS build
WORKDIR /src
COPY requirements.txt .
RUN mkdir /install && pip install --no-cache-dir --prefix=/install -r requirements.txt
COPY scd_ingestion ./scd_ingestion
RUN PYTHONPATH=/install/lib/python3.12/site-packages:/src MODEL_DIR=/src/model MODEL_DOWNLOAD=1 \
    python -c "from scd_ingestion.embed import embed; assert len(embed(['check'])[0]) == 384"

FROM python:3.12-slim@sha256:5b5fe805d367f8f5a359ded6ab2652b7f9a206453ee6ee789c0045ba6ec15016
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1
WORKDIR /app
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*
COPY --from=build /install /usr/local
COPY --from=build /src/model ./model
COPY --from=build /src/scd_ingestion ./scd_ingestion
USER 10001:10001
CMD ["python", "-m", "scd_ingestion.job"]
