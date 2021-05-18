FROM node:alpine

ENV HOME /root
ENV INSTALLATION_DIR /home/pi/RPi-Jukebox-RFID

WORKDIR ${INSTALLATION_DIR}/webapp

ENV PATH ${INSTALLATION_DIR}/webapp/node_modules/.bin:$PATH

COPY ./src/webapp/package*.json ./

RUN npm install
RUN npm install react-scripts@3.4.1 -g

COPY ./src/webapp ./

CMD ["npm", "start"]