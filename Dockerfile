FROM python:3.14-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python3", "bot_server.py"]
