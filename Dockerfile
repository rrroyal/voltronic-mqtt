FROM debian:bullseye

RUN apt update -y
#RUN apt upgrade -y
RUN apt install -y \
		python3 \
		python3-pip \
		python3-setuptools
RUN rm -rf /var/lib/apt/lists/*
RUN pip3 install --upgrade pip

COPY src/ /app/
COPY requirements.txt /app/

RUN cd /app && pip3 install -r requirements.txt

WORKDIR /app
ENTRYPOINT ["/bin/bash", "/app/run.sh"]

#EXPOSE 1883
