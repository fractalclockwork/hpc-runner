FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY src ./src
COPY configs ./configs
# LAMMPS smoke input for lammps-slurm solver (see docs/TESTING_SLURM.md)
COPY docker/lammps ./docker/lammps

RUN uv sync --frozen --all-extras --dev

EXPOSE 8000
CMD ["uv", "run", "basic-restapi"]
