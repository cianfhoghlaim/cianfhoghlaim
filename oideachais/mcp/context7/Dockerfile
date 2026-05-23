FROM node:18-alpine
WORKDIR /app
# Install the necessary packages globally within the container
RUN npm install -g @upstash/context7-mcp@latest
# Default command to run when the container starts
CMD ["context7-mcp"]
