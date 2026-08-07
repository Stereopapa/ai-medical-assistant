FROM python:3.12-slim

# Kopiujemy gotowy, bardzo szybki plik wykonywalny uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Definiujemy wirtualne środowisko, z którego domyślnie korzysta uv i PyCharm
ENV VIRTUAL_ENV=/workspace/.venv
ENV PATH="/workspace/.venv/bin:$PATH"
ENV UV_COMPILE_BYTECODE=1

# Tworzymy virtualenv przy budowaniu obrazu
RUN uv venv