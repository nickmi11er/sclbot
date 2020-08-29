FROM alpine:latest
RUN apk add --update python2 sqlite
RUN python -m ensurepip
RUN pip install --upgrade pip

COPY requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt

COPY src /src
COPY assets/schema.sql /assets/schema.sql

CMD python /src/bot.py