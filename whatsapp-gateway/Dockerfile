FROM node:24-bookworm-slim
WORKDIR /app
COPY whatsapp-gateway/package*.json ./
RUN npm ci --omit=dev
COPY whatsapp-gateway/*.js ./
RUN mkdir /state && chown node:node /state
USER node
CMD ["node","src.js"]
