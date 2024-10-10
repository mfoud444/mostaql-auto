# Stage 1: Build dependencies
FROM python:3-alpine AS builder

WORKDIR /app

# Set up virtual environment
RUN python3 -m venv venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY . .

# Install system dependencies using apk
RUN apk add --no-cache \
    bash \
    build-base \
    boost-dev \
    cmake \
    python3-dev \
    py3-pip \
    libexecinfo-dev

# Then continue with Python package installations
RUN pip install -U deep-translator
RUN pip install -r requirements.txt

# Stage 2: Runner
FROM python:3-alpine AS runner

WORKDIR /app

COPY --from=builder /app/venv venv
COPY . .

ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

EXPOSE 7860

CMD ["python3", "app.py"]
