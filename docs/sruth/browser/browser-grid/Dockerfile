# Patchright-based Stealth Browser Grid
# Based on: Open-Source Crawl4ai Anti-Bot Stack.md
#
# Provides CDP (Chrome DevTools Protocol) endpoint for:
# - Crawl4AI bulk extraction
# - Stagehand agentic reconnaissance
# - Turnstile solver automation

FROM node:20-bullseye-slim

# Install system dependencies for Chromium
RUN apt-get update && apt-get install -y \
    # Core dependencies
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
    # Virtual display for headless operation
    xvfb \
    # Fonts for rendering
    fonts-noto-color-emoji \
    fonts-freefont-ttf \
    # Utilities
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install Patchright (stealth Playwright fork)
RUN npm install patchright

# Install Patchright's Chromium with stealth patches
RUN npx patchright install chromium

# Copy launch script
COPY launch.js .

# Expose CDP port
EXPOSE 9222

# Start with virtual framebuffer for headless operation
CMD ["xvfb-run", "--server-args=-screen 0 1920x1080x24", "node", "launch.js"]
