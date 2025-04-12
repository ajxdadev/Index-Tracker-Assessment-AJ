# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install pip requirements
COPY requirements.txt /app/requirements.txt
RUN python -m pip install -r requirements.txt

RUN echo "Root context:" && ls -al /app

COPY ./backend-service backend-service
WORKDIR /app/backend-service
#COPY backend-service/app /app/app
#COPY backend-service/main.py /app/main.py


# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
#RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
#USER appuser
EXPOSE 8000
# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "main:app"]
