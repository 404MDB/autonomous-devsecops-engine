FROM node:20-bookworm-slim

WORKDIR /app

COPY package*.json ./

RUN npm ci --only=production

COPY server.js ./

EXPOSE 3000

CMD ["node", "server.js"]
