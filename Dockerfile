FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apk add --update py-pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "./s06.py"]

ENTRYPOINT ["python"]