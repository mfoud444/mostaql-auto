FROM python:3-alpine AS builder
 
WORKDIR /app
 
RUN python3 -m venv venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
 
COPY . .
RUN pip install -r requirements.txt
RUN pip install --upgrade together
# Stage 2
FROM python:3-alpine AS runner
 
WORKDIR /app
 
COPY --from=builder /app/venv venv
COPY . .
 
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
# ENV FLASK_APP=app/app.py
 
EXPOSE 7860
 
CMD ["python3", "app-boot.py"]
# CMD ["gunicorn", "--bind" , ":8080", "--workers", "2", "app:app"]