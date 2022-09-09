FROM python:3.9

RUN apt-get update && apt-get install -y \
	xvfb

COPY src/* ./
COPY src/hippogym_app/images/* ./images/
COPY src/hippogym_app/Fingerprints/* ./Fingerprints/
RUN mkdir ./Trials
RUN mkdir ./XML
COPY requirements.txt .

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD ./xvfb.sh
