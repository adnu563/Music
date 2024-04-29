FROM nikolaik/python-nodejs:python3.10-nodejs19

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . /app/
WORKDIR /app/
RUN pip3 install --no-cache-dir -U -r requirements.txt

CMD bash start
# Use an official Python runtime as a parent image
FROM python:3.9-slim

RUN pip install --no-cache-dir -r requirements.txt

# Run the bot when the container launches
CMD ["python3", "userinfo.py"]
