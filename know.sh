#!/bin/bash

# Project setup script for Secure Terminal Emulator Server

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Create project directory
PROJECT_NAME="secure-terminal-server"
mkdir $PROJECT_NAME
cd $PROJECT_NAME

echo -e "${GREEN}Creating project structure...${NC}"

# Create directory structure
mkdir -p config models routes middleware services

# Initialize Node.js project
echo -e "${GREEN}Initializing Node.js project...${NC}"
npm init -y

# Install dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
npm install express mongoose socket.io bcrypt jsonwebtoken dotenv helmet express-rate-limit ioredis socket.io-redis joi

# Create .env file
echo -e "${GREEN}Creating .env file...${NC}"
cat << EOF > .env
PORT=3000
MONGODB_URI=mongodb://localhost/secure_terminal_db
JWT_SECRET=change_this_to_a_secure_random_string
NODE_ENV=development
EOF

# Create .gitignore
echo -e "${GREEN}Creating .gitignore...${NC}"
cat << EOF > .gitignore
node_modules/
.env
*.log
EOF

# Create basic files
echo -e "${GREEN}Creating basic template files...${NC}"

# config/database.js
cat << EOF > config/database.js
const mongoose = require('mongoose');

module.exports = async () => {
  try {
    await mongoose.connect(process.env.MONGODB_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
      useCreateIndex: true
    });
    console.log('Connected to MongoDB');
  } catch (error) {
    console.error('MongoDB connection error:', error);
    process.exit(1);
  }
};
EOF

# models/User.js
cat << EOF > models/User.js
const mongoose = require('mongoose');

const UserSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  role: { type: String, default: 'user' }
});

module.exports = mongoose.model('User', UserSchema);
EOF

# models/Config.js
cat << EOF > models/Config.js
const mongoose = require('mongoose');

const ConfigSchema = new mongoose.Schema({
  envName: String,
  ringEnabled: Boolean,
  ringColor: String,
  ringText: String,
  ringSpeed: Number,
  enforceCommandValidation: Boolean,
  enableImmutableLogging: Boolean,
  createdBy: String,
  sharedWith: [String]
});

module.exports = mongoose.model('Config', ConfigSchema);
EOF

# models/Log.js
cat << EOF > models/Log.js
const mongoose = require('mongoose');

const LogSchema = new mongoose.Schema({
  username: String,
  command: String,
  timestamp: { type: Date, default: Date.now },
  environment: String
});

module.exports = mongoose.model('Log', LogSchema);
EOF

# middleware/auth.js
cat << EOF > middleware/auth.js
const jwt = require('jsonwebtoken');

module.exports = (req, res, next) => {
  const token = req.header('x-auth-token');
  if (!token) return res.status(401).json({ message: 'No token, authorization denied' });

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    res.status(401).json({ message: 'Token is not valid' });
  }
};
EOF

# middleware/errorHandler.js
cat << EOF > middleware/errorHandler.js
module.exports = (err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ message: 'Something went wrong' });
};
EOF

# services/socketio.js
cat << EOF > services/socketio.js
const socketIo = require('socket.io');
const redis = require('socket.io-redis');

module.exports = (server) => {
  const io = socketIo(server);
  io.adapter(redis({ host: 'localhost', port: 6379 }));

  io.on('connection', (socket) => {
    console.log('New client connected');

    socket.on('subscribe', (configId) => {
      socket.join(configId);
    });

    socket.on('configUpdate', async (data) => {
      // Implement config update logic
    });

    socket.on('disconnect', () => {
      console.log('Client disconnected');
    });
  });

  return io;
};
EOF

# server.js
cat << EOF > server.js
require('dotenv').config();
const express = require('express');
const https = require('https');
const fs = require('fs');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const errorHandler = require('./middleware/errorHandler');
const connectDB = require('./config/database');
const socketService = require('./services/socketio');

const app = express();

// Security middleware
app.use(helmet());
app.use(rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100
}));

app.use(express.json());

// Connect to database
connectDB();

// Routes
app.use('/api/auth', require('./routes/auth'));
app.use('/api/configs', require('./routes/configs'));
app.use('/api/logs', require('./routes/logs'));

// Error handling
app.use(errorHandler);

// HTTPS server
// Note: You need to generate your own SSL certificates
/*
const server = https.createServer({
  key: fs.readFileSync('path/to/key.pem'),
  cert: fs.readFileSync('path/to/cert.pem')
}, app);
*/

// For development, use HTTP
const server = require('http').createServer(app);

// Socket.IO setup
const io = socketService(server);

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(\`Server running on port \${PORT}\`));

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM signal received: closing HTTP server');
  server.close(() => {
    console.log('HTTP server closed');
    process.exit(0);
  });
});
EOF

# Create empty route files
touch routes/auth.js routes/configs.js routes/logs.js

echo -e "${GREEN}Project setup complete!${NC}"
echo -e "${GREEN}To start the project:${NC}"
echo -e "1. cd $PROJECT_NAME"
echo -e "2. npm install"
echo -e "3. node server.js"
echo -e "${GREEN}Remember to implement the route logic in the routes/ directory and set up your MongoDB database.${NC}"
