FROM python:3.7
MAINTAINER lijian@ooclab.com

ENV PATH /usr/local/bin:$PATH

COPY requirements.txt /
RUN pip3 install -r /requirements.txt && rm /requirements.txt
COPY src /work

VOLUME /data
WORKDIR /work

EXPOSE 3000

CMD ["python3", "server.py"]
