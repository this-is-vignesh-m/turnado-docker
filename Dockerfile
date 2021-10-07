# FROM python:3.7
# EXPOSE 8888

# RUN mkdir -p /usr/src/app
# WORKDIR /usr/src/app

# COPY requirements.txt /usr/src/app/
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# ENTRYPOINT ["python3", "app.py"]

FROM python:3.8
ENV PYTHONUNBUFFED 1
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/
RUN python3 -m pip install -r requirements.txt
COPY . /app/
