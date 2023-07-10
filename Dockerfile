FROM python:3.10.6-bullseye

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

RUN pip3 install --upgrade pip

COPY . /usr/src/app

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--log-level", "critical","--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
