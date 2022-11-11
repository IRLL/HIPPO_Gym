FROM python:3.7

RUN apt-get update && apt-get install -y \
	xvfb \
	python-opengl

COPY App/* ./
COPY App/images/* ./images/
COPY App/Fingerprints/* ./Fingerprints/
COPY App/MtiaeScoreAgent/* ./
COPY App/MtiaeScoreAgent/Impressions/* ./Impressions/
RUN mkdir ./Trials
COPY requirements.txt .

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD ./xvfb.sh
