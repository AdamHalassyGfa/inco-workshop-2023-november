FROM python:latest

WORKDIR /opt/scraper

COPY *.py ./
COPY lib/*.py ./lib/
ADD ./*.py /opt/scraper/
ADD ./*.py /opt/scraper/lib/

RUN python3 -m ensurepip --default-pip
RUN python3 -m venv /opt/scraper/
RUN python3 -m pip install lxml requests

ENTRYPOINT [ "python", "-u", "/opt/scraper/scraper.py" ]
