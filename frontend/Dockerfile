FROM node:20-alpine AS front
WORKDIR /app

COPY package*.json .
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=front /app/dist /usr/share/nginx/html
COPY ./nginx-spa.conf /etc/nginx/nginx.conf
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]