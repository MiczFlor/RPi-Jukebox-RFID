FROM node:18-bullseye-slim

USER node
RUN mkdir -p /home/node/webapp
WORKDIR /home/node/webapp

COPY --chown=node:node ./src/webapp ./

RUN npm install

CMD ["npm", "start"]
