FROM python:3-alpine AS builder
 
WORKDIR /app
 
RUN python3 -m venv venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
 
COPY . .
# Install system dependencies
RUN apt-get update && apt-get install -y \
    libboost-filesystem-dev \
    libboost-system-dev \
    cmake \
    build-essential \
    libarrow-dev \
    libarrow-python-dev \
    python3-dev \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Then continue with Python package installations
RUN pip install -U deep-translator
RUN pip install -r requirements.txt

RUN pip install -U deep-translator
# Stage 2
FROM python:3-alpine AS runner
 
WORKDIR /app
 
COPY --from=builder /app/venv venv
COPY . .
 
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
# ENV FLASK_APP=app/app.py
 
EXPOSE 7860
 
CMD ["python3", "app.py"]
# CMD ["gunicorn", "--bind" , ":8080", "--workers", "2", "app:app"]