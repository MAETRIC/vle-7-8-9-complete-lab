FROM node:22-alpine
RUN rm -rf /usr/local/lib/node_modules /opt/yarn* /usr/local/bin/npm /usr/local/bin/npx /usr/local/bin/yarn* /usr/local/bin/corepack
WORKDIR /app
COPY --chown=node:node package.json server.js ./
USER node
EXPOSE 8080
CMD ["node", "server.js"]
