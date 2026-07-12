# Patchright-based Stealth Browser Grid

FROM node:20-bullseye-slim

RUN apt-get update && apt-get install -y \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    xvfb \
    fonts-noto-color-emoji \
    fonts-freefont-ttf \
    curl \
    ca-certificates \
    socat \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN npm install patchright node-fetch@2

RUN npx patchright install chromium

COPY launch.js .

EXPOSE 9222 9223

CMD ["xvfb-run", "--server-args=-screen 0 1920x1080x24", "node", "launch.js"]
