FROM node:20-alpine AS build
WORKDIR /app
# copy package files first for cached deps
COPY package.json package-lock.json* ./
# use npm ci for reproducible installs and allow legacy peer deps if needed
RUN npm ci --legacy-peer-deps --no-audit --progress=false
COPY . .
# build the app (needs devDependencies like typescript)
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
