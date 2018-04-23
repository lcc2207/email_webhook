FROM debian:jessie-slim
MAINTAINER Scalr <@scalr.com>

RUN apt-get update && \
    apt-get install -y --no-install-recommends python python-dev python-pip uwsgi uwsgi-plugin-python && \
    groupadd uwsgi && \
    useradd -g uwsgi uwsgi

COPY ./requirements.txt /opt/email-webhook/

RUN pip install -r /opt/email-webhook/requirements.txt

COPY . /opt/email-webhook

EXPOSE 5000

CMD ["/usr/bin/uwsgi", "--ini", "/opt/email-webhook/uwsgi.ini"]
