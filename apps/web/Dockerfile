FROM node:22-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source and build
COPY . .
RUN npm run build

# Production server
FROM nginx:alpine
# Copy built static files to Nginx public folder
COPY --from=builder /app/dist /usr/share/nginx/html
# Override server config to support larger upload bodies.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port and start nginx
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
