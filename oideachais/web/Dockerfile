FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 80 3000
CMD ["npm", "run", "dev", "--", "--host"]
