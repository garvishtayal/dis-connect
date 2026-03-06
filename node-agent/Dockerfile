FROM node:22-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY . .

EXPOSE 3000

# Expect a "start" script in package.json
CMD ["npm", "run", "start"]

