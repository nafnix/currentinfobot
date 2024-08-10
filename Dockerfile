# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.11
FROM curlimages/curl AS just-fetcher

RUN curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | sh -s -- --to /tmp

FROM python:${PYTHON_VERSION}-slim-bookworm

COPY --from=just-fetcher /tmp/just /usr/bin/just

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

ARG PYPI_MIRROR=https://pypi.org/simple


# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade -i ${PYPI_MIRROR} uv


ARG INSTALL_DEV=true \
    UV_SYSTEM_PYTHON=true \
    UV_INDEX_URL=${PYPI_MIRROR}

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    --mount=type=bind,source=requirements.dev.txt,target=requirements.dev.txt \
    if $INSTALL_DEV == 'true' ; then uv pip install -r requirements.dev.txt ; fi && \
    uv pip install -r requirements.txt


# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container.
COPY . .


CMD ["just", "run"]
