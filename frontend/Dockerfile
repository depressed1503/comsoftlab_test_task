FROM node:latest AS frontend
WORKDIR /app

RUN npm install -g serve

COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build
