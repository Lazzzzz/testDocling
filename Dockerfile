FROM python:3.11.3
ENV PYTHONUNBUFFERED True

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set application environment variables
ENV APP_HOME /root
ENV PORT 8080  # Default port for Cloud Run

WORKDIR $APP_HOME
COPY ./app $APP_HOME/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
