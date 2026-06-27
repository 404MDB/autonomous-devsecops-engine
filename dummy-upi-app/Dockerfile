# 1. Use an LTS (Long Term Support) version, not an EOL version
FROM node:20-alpine

# 2. Set non-root user for security (Best Practice)
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
WORKDIR /usr/src/app

# 3. Copy lockfile first to leverage Docker layer caching correctly
COPY package*.json ./

# 4. Install dependencies and clean up cache in one step to keep image size small
RUN apk add --no-cache python3 make g++ && \
    npm ci --only=production && \
    npm cache clean --force && \
    apk del python3 make g++

# 5. Copy app code and set ownership
COPY . .
RUN chown -R appuser:appgroup /usr/src/app

# 6. Switch to non-root user
USER appuser

EXPOSE 3000
CMD ["node", "server.js"]