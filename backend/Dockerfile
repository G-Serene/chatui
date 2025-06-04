# Use an official Node.js runtime as a parent image
FROM node:lts-alpine
WORKDIR /usr/src/app

# Copy package.json, package-lock.json (if available), and tsconfig.json
# These are copied separately to leverage Docker cache
COPY package.json ./
COPY package-lock.json* ./
COPY tsconfig.json ./

# Install app dependencies
# Using npm ci for reproducible builds, ensuring it only installs production dependencies
# If your npm version is old, `npm ci --omit=dev` might not work, use `npm install --production`
RUN npm ci --omit=dev

# Bundle app source
COPY src ./src

# Compile TypeScript to JavaScript
# Ensure your tsconfig.json has "outDir": "./dist" or similar
RUN npm run build || npx tsc

# Expose port and define command to run the app
EXPOSE 3001
CMD ["node", "dist/index.js"]
