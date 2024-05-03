FROM node:20-alpine

USER node
RUN mkdir -p /home/node/webapp
WORKDIR /home/node/webapp

COPY --chown=node:node ./src/webapp ./

RUN npm install

CMD ["npm", "start"]
