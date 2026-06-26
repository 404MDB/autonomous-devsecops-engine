# Intentionally using an older, vulnerable Node base image for SCA testing
FROM node:14-alpine

WORKDIR /usr/src/app

COPY package*.json ./

# Install python and build tools needed to compile native modules (sqlite3)
RUN apk add --no-cache python3 make g++ && \
    npm install && \
    apk del python3 make g++

COPY . .

EXPOSE 3000
CMD ["node", "server.js"]
