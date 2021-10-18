FROM node:alpine

USER node
RUN mkdir -p /home/node/webapp
WORKDIR /home/node/webapp

COPY --chown=node:node ./src/webapp/package*.json ./

RUN npm install

COPY --chown=node:node ./src/webapp ./

CMD ["npm", "start"]
