FROM node:18
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --silent || npm install
COPY . .
CMD ["npm", "run", "dev"]
