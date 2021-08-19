FROM python:3.7

RUN apt-get update && apt-get install -y \
	xvfb

COPY App/* ./
COPY App/images/* ./images/
COPY App/Fingerprints/* ./Fingerprints/
RUN mkdir ./Trials
RUN mkdir ./XML
COPY requirements.txt .

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD ./xvfb.sh
