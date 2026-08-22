FROM python:3.12-slim-bookworm

WORKDIR /app

RUN useradd --system --uid 10001 --no-create-home mct \
    && mkdir -p /app && chown mct:mct /app

COPY --chown=mct:mct . .

USER 10001
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MCT_CYCLES=0

STOPSIGNAL SIGTERM

CMD ["python", "run_loop.py"]
