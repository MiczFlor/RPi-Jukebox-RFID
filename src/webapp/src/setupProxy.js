const { createProxyMiddleware } = require('http-proxy-middleware');

const target = process.env.API_PROXY_TARGET || 'http://localhost:5556';

module.exports = function setupProxy(app) {
  app.use(createProxyMiddleware('/api', {
    target,
    ws: true,
    changeOrigin: false,
  }));
};
