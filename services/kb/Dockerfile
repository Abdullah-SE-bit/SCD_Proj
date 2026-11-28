# Debian, not Alpine: the model runtime has no musl build. Both models are downloaded at build time because the
# service has no internet access in the cluster.
FROM python:3.12-slim@sha256:5b5fe805d367f8f5a359ded6ab2652b7f9a206453ee6ee789c0045ba6ec15016 AS build
WORKDIR /src
COPY requirements.txt .
RUN mkdir /install && pip install --no-cache-dir --prefix=/install -r requirements.txt
COPY scd_kb ./scd_kb
RUN PYTHONPATH=/install/lib/python3.12/site-packages:/src MODEL_DIR=/src/model MODEL_DOWNLOAD=1     python -c "from scd_kb import models; assert len(models.embed('check')) == 384; models.rerank('a', ['b'])"

FROM python:3.12-slim@sha256:5b5fe805d367f8f5a359ded6ab2652b7f9a206453ee6ee789c0045ba6ec15016
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1
WORKDIR /app
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*
COPY --from=build /install /usr/local
COPY --from=build --chmod=755 /src/model ./model
COPY --from=build /src/scd_kb ./scd_kb
USER 10001:10001
EXPOSE 8000
CMD ["python", "-m", "scd_kb.app"]
