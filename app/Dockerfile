FROM python:3.9

COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt

RUN apt update && apt install -y netcat

RUN chown nobody -R /app

USER nobody

RUN chmod +x entry.sh

ENTRYPOINT ["./entry.sh"]