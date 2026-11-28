FROM python:3.12-alpine@sha256:c5ba3deef00c7758561a0f03c26f44f10589263d40e732b8748e0d1f38f6dd89 AS build
WORKDIR /src
COPY requirements.txt .
RUN mkdir /install && pip install --no-cache-dir --prefix=/install -r requirements.txt
COPY scd_ideation ./scd_ideation

FROM python:3.12-alpine@sha256:c5ba3deef00c7758561a0f03c26f44f10589263d40e732b8748e0d1f38f6dd89
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY --from=build /install /usr/local
COPY --from=build /src/scd_ideation ./scd_ideation
USER 10001:10001
EXPOSE 8000
CMD ["python", "-m", "scd_ideation.app"]
