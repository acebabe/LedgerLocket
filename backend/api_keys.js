// Example API key + permission middleware for LedgerLocket
// WARNING: This file contains an example API key. Do NOT commit real API keys in source.
// Move keys to a secure store or use environment variables in production.

const apiKeys = new Map([
  ['token_6LjoYEvy9LiYektzQ04r67At1tYeUB5g', {
    permissions: ['users:delete', 'users:read', 'posts:read', 'users:write', 'posts:write', 'comments:write', 'posts:delete', 'payments:process', 'media:delete', 'payments:refund', 'media:upload', 'admin:settings', 'webhooks:create', 'admin:audit', 'webhooks:delete', 'analytics:export', 'comments:moderate', 'comments:read', 'payments:read', 'analytics:read'],
    rate_limit: '1000/hour',
    api_version: 'beta'
  }]
]);

function requirePermission(requiredPermission) {
  return (req, res, next) => {
    const apiKey = req.headers['authorization']?.replace('Bearer ', '');
    
    if (!apiKey) {
      return res.status(401).json({ error: 'API key required' });
    }
    
    const keyData = apiKeys.get(apiKey);
    if (!keyData) {
      return res.status(401).json({ error: 'Invalid API key' });
    }
    
    // Check permission
    const hasPermission = keyData.permissions.includes('*:*') || 
                         keyData.permissions.includes(requiredPermission);
    
    if (!hasPermission) {
      return res.status(403).json({ 
        error: 'Insufficient permissions',
        required: requiredPermission,
        granted: keyData.permissions
      });
    }
    
    req.apiKey = keyData;
    next();
  };
}

module.exports = { apiKeys, requirePermission };

// Usage example (Express):
// const express = require('express');
// const app = express();
// const { requirePermission } = require('./backend/api_keys');
//
// app.get('/users', requirePermission('users:read'), (req, res) => {
//   res.json({ users: [] });
// });
//
// app.post('/users', requirePermission('users:write'), (req, res) => {
//   res.json({ message: 'User created' });
// });
