# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app
# Accept build argument for API URL
ARG REACT_APP_API_URL=https://cairogenizah.ai
ENV REACT_APP_API_URL=$REACT_APP_API_URL

# Debug: Show what API URL is being used
RUN echo "Building with API URL: $REACT_APP_API_URL"

# Copy package files
COPY package.json ./
RUN npm install --omit=dev

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Use nginx to serve the built app
FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
COPY  nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]