FROM python:3.9

RUN apt-get update && apt-get install -y \
	xvfb \
	swig
WORKDIR /src/hippogym

COPY src/hippogym .
COPY examples /src/hippogym/examples

RUN mkdir ../Trials

COPY requirements.txt .
COPY requirements-examples.txt .

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN pip3 install -r requirements-examples.txt
RUN pip3 install pyopengl

ENV PYTHONPATH "${PYTHONPATH}:/src"
EXPOSE 5000

COPY start.sh ./
CMD ./start.sh
