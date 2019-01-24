FROM alpine:latest
RUN apk add --update python py-pip sqlite

COPY requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt

COPY src /src
COPY assets/schema.sql /assets/schema.sql

CMD python /src/bot.py