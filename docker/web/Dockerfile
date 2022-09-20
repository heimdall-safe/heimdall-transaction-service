FROM python:3.10-slim

ARG APP_HOME=/app
WORKDIR ${APP_HOME}
ENV PYTHONUNBUFFERED=1

# https://eth-hash.readthedocs.io/en/latest/quickstart.html#specify-backend-by-environment-variable
# `pysha3` is way faster than `pycryptodome` for CPython
ENV ETH_HASH_BACKEND=pysha3
ENV ETHEREUM_NODE_URL=https://eth.bd.evmos.org:8545
ENV ETHEREUM_TRACING_NODE_URL=https://eth.bd.evmos.org:8545
ENV DATABASE_URL=postgres://postgres:BsIlZRoVe6fqbVSPiOnT@mydb.c51vxpmor1au.us-west-1.rds.amazonaws.com:5432/postgres
COPY requirements.txt ./
RUN set -ex \
	&& buildDeps=" \
		build-essential \
        git \
		libssl-dev \
        libpq-dev \
		" \
    && apt-get update \
    && apt-get install -y --no-install-recommends $buildDeps tmux postgresql-client \
    && pip install -U --no-cache-dir wheel setuptools pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove $buildDeps \
    && rm -rf /var/lib/apt/lists/* \
    && find /usr/local \
        \( -type d -a -name test -o -name tests \) \
        -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
        -exec rm -rf '{}' +

COPY . .
CMD ["python3", "manage.py", "collectstatic", "makemigrations", "migrate", "runserver", "0.0.0.0:8000"]
