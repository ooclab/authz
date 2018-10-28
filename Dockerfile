FROM python:3.7-alpine
MAINTAINER info@ooclab.com

ENV PYTHONIOENCODING=utf-8
ENV PYTHONPATH=/work
ENV PATH /usr/local/bin:$PATH

COPY src /work
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt \
    && rm -f requirements.txt

VOLUME /data
WORKDIR /work

EXPOSE 3000

CMD ["python3", "server.py"]
