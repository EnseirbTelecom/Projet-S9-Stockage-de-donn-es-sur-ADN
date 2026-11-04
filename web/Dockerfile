FROM node:22-alpine

WORKDIR /app

# Installation des dépendances
COPY package*.json ./

RUN npm install

# Copie du frontend
COPY . .

# Port Vite
EXPOSE 3000

# Démarrage du serveur React
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]