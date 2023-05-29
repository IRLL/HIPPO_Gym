FROM python:3.9

RUN apt-get update && apt-get install -y \
	xvfb \
	swig \
	libsdl2-mixer-2.0-0
WORKDIR /src/hippogym

COPY src/hippogym .
COPY examples /src/hippogym/examples

RUN mkdir ../Trials

COPY requirements.txt .
COPY requirements-examples.txt .

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN pip3 install -r requirements-examples.txt
RUN pip3 install pyopengl==3.1.6

ENV PYTHONPATH "${PYTHONPATH}:/src"
ENV SDL_VIDEODRIVER dummy
ENV SDL_AUDIODRIVER dummy

ENV DISPLAY :99

ENV HIPPOGYM_HOST 0.0.0.0
EXPOSE 5000

COPY start.sh ./
CMD ./start.sh
