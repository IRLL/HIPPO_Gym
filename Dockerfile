FROM python:3.7

# Add 32-bit architecture
RUN dpkg --add-architecture i386

RUN apt-get update && apt-get install -y \
	xvfb \
	python-opengl \
	wine \
	wine32 \
	wine64 \
	libwine \
	libwine:i386 \
	fonts-wine

# Turn off Fixme warnings
ENV WINEDEBUG=fixme-all

# Install Mono
RUN wget -P /mono http://dl.winehq.org/wine/wine-mono/4.9.4/wine-mono-4.9.4.msi
RUN wineboot -u && msiexec /i /mono/wine-mono-4.9.4.msi
RUN rm -rf /mono/wine-mono-4.9.4.msi

COPY App/* ./
COPY App/images/* ./images/
COPY App/MtiaeScoreAgent/* ./
COPY App/MtiaeScoreAgent/Impressions/* ./Impressions/
RUN mkdir ./Trials
RUN mkdir ./XML
COPY requirements.txt .

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD ./xvfb.sh
