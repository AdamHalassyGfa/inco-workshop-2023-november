FROM python:latest

WORKDIR /opt/workshop

COPY *.py ./
COPY lib/*.py ./lib/
COPY data.db ./

ADD ./*.py /opt/workshop
ADD ./data.db /opt/workshop

RUN python3 -m ensurepip --default-pip
RUN python3 -m venv /opt/workshop/
RUN python3 -m pip install flask

ENTRYPOINT [ "python", "-u", "/opt/workshop/webapp.py" ]
