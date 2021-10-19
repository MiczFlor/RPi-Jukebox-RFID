FROM node:alpine

WORKDIR /home/node/webapp

COPY ./src/webapp ./

RUN npm install

CMD ["npm", "start"]
