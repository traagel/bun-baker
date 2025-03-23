#!/bin/bash

SERVICE_NAME=$1

if [ -z "$SERVICE_NAME" ]; then
  echo "Usage: $0 <service-name>"
  exit 1
fi

# Create directory structure
mkdir -p ${SERVICE_NAME}/{src/{data-access,models,routes,schemas,utils,db/migrations,plugins},docs,scripts}

# Generate base files
cat >${SERVICE_NAME}/.gitignore <<EOF
node_modules
dist
.env
*.log
EOF

cat >${SERVICE_NAME}/tsconfig.json <<EOF
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "node",
    "esModuleInterop": true,
    "strict": true,
    "outDir": "./dist",
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
EOF

cat >${SERVICE_NAME}/package.json <<EOF
{
  "type": "module",
  "name": "${SERVICE_NAME}-service",
  "version": "1.0.0",
  "scripts": {
    "build": "bun build ./src/app.ts --outdir=./dist --target node",
    "start": "bun run dist/app.js",
    "dev": "bun run --watch src/app.ts",
    "migrate": "bun run src/db/migrate.ts",
    "migrate:reset": "bun run src/db/migrate.ts reset",
    "postdeploy": "bun run migrate"
  },
  "dependencies": {
    "@fastify/auth": "latest",
    "@fastify/cors": "latest",
    "@fastify/jwt": "latest",
    "@fastify/rate-limit": "latest",
    "@fastify/swagger": "^9.4.2",
    "@fastify/swagger-ui": "^5.2.1",
    "@fastify/type-provider-typebox": "^5.1.0",
    "@sinclair/typebox": "latest",
    "bcrypt": "latest",
    "dotenv": "latest",
    "fastify": "latest",
    "jose": "^5.9.6",
    "pg-promise": "latest",
    "pino": "latest",
    "pino-pretty": "latest",
    "typescript": "latest"
  },
  "devDependencies": {
    "@types/bcrypt": "latest",
    "@types/node": "latest"
  },
  "engines": {
    "node": ">=20.0.0",
    "bun": ">=0.6.0"
  }
}
EOF

cat >${SERVICE_NAME}/Dockerfile <<EOF
FROM oven/bun:latest

WORKDIR /app

COPY package.json bun.lockb ./
RUN bun install --production

COPY . .

RUN bun run build

EXPOSE 3000

CMD ["bun", "run", "start"]
EOF

# Core application files
cat >${SERVICE_NAME}/src/app.ts <<EOF
import fastify, { FastifyInstance } from 'fastify';
import { TypeBoxTypeProvider } from '@fastify/type-provider-typebox';
import { config } from '@/config';
import { errorHandler } from '@/utils/errorHandler';
import { sanitizeRequestBody } from '@/utils/sanitizer';
import { registerPlugins } from '@/plugins';
import { registerRoutes } from '@/routes';

const buildApp = async (): Promise<FastifyInstance> => {
  const app = fastify({
    logger: config.logger,
  }).withTypeProvider<TypeBoxTypeProvider>();

  try {
    await registerPlugins(app);

    app.addHook('preHandler', (request, reply, done) => {
      sanitizeRequestBody(request);
      done();
    });

    app.setErrorHandler(errorHandler);

    app.decorate('authenticate', async (request, reply) => {
      try {
        await request.jwtVerify({
          algorithms: ['RS256'],
          issuer: config.jwt.issuer,
          audience: config.jwt.audience
        });
      } catch (err) {
        request.log.error(err, 'Authentication error');
        reply.code(401).send({ 
          error: 'Authentication failed',
          ...(process.env.NODE_ENV === 'development' && { details: err.message })
        });
      }
    });

    await registerRoutes(app);
    app.log.info('All plugins and routes registered');
  } catch (err) {
    app.log.error('Error during app initialization:', err);
    throw err;
  }

  return app;
};

const startServer = async () => {
  try {
    const app = await buildApp();
    await app.listen({ port: config.port, host: '0.0.0.0' });
    console.log(\`Server is running on http://localhost:\${config.port}\`);
  } catch (err) {
    console.error('Failed to start server:', err);
    process.exit(1);
  }
};

startServer();
EOF

# Config
mkdir -p ${SERVICE_NAME}/src/config
cat >${SERVICE_NAME}/src/config.ts <<EOF
import dotenv from 'dotenv';

dotenv.config();

export const config = {
  port: parseInt(process.env.PORT || '3000'),
  logger: {
    level: process.env.LOG_LEVEL || 'info',
    prettyPrint: process.env.NODE_ENV === 'development'
  },
  jwt: {
    jwksUri: process.env.JWT_JWKS_URI || 'https://auth-service/.well-known/jwks.json',
    issuer: process.env.JWT_ISSUER || 'fairytale-auth-service',
    audience: process.env.JWT_AUDIENCE || 'fairytale-realm'
  },
  database: {
    url: process.env.DATABASE_URL || 'postgres://postgres:postgres@localhost:5432/${SERVICE_NAME}_db'
  }
};
EOF

# Utilities
mkdir -p ${SERVICE_NAME}/src/utils
cat >${SERVICE_NAME}/src/utils/errorHandler.ts <<EOF
import { FastifyError, FastifyReply, FastifyRequest } from 'fastify';

export const errorHandler = (
  error: FastifyError,
  request: FastifyRequest,
  reply: FastifyReply
) => {
  const statusCode = error.statusCode || 500;
  const message = statusCode === 500 ? 'Internal Server Error' : error.message;
  
  request.log.error(error);
  
  reply.status(statusCode).send({
    error: message,
    ...(process.env.NODE_ENV === 'development' && {
      details: error.message,
      stack: error.stack
    })
  });
};
EOF

cat >${SERVICE_NAME}/src/utils/sanitizer.ts <<EOF
import { FastifyRequest } from 'fastify';

export const sanitizeRequestBody = (request: FastifyRequest) => {
  if (request.body) {
    // Sanitization logic here
  }
};
EOF

# Plugins
mkdir -p ${SERVICE_NAME}/src/plugins
cat >${SERVICE_NAME}/src/plugins/index.ts <<EOF
import { FastifyInstance } from 'fastify';
import { createRemoteJWKSet } from 'jose';
import { config } from '@/config';

export async function registerPlugins(app: FastifyInstance) {
  const jwks = createRemoteJWKSet(new URL(config.jwt.jwksUri));

  await app.register(import('@fastify/swagger'), {
    openapi: {
      info: {
        title: '${SERVICE_NAME} Service',
        description: 'Microservice API Documentation',
        version: '1.0.0'
      },
      servers: [{
        url: \`http://localhost:\${config.port}\`,
        description: 'Development server'
      }],
      components: {
        securitySchemes: {
          bearerAuth: {
            type: 'http',
            scheme: 'bearer',
            bearerFormat: 'JWT'
          }
        }
      }
    },
    hideUntagged: true
  });

  await app.register(import('@fastify/swagger-ui'), {
    routePrefix: '/docs',
    uiConfig: {
      docExpansion: 'list',
      deepLinking: false
    }
  });

  await app.register(import('@fastify/cors'));
  
  await app.register(import('@fastify/jwt'), {
    decode: { complete: true },
    secret: (header, callback) => {
      jwks(header, callback)
    },
    verify: {
      issuer: config.jwt.issuer,
      audience: config.jwt.audience
    }
  });
}
EOF

# Routes
mkdir -p ${SERVICE_NAME}/src/routes
cat >${SERVICE_NAME}/src/routes/index.ts <<EOF
import { FastifyInstance } from 'fastify';
import { healthRoutes } from '@/routes/health';

export const registerRoutes = async (app: FastifyInstance) => {
  try {
    app.get('/openapi.json', { }, async () => app.swagger());

    app.get('/', {
      schema: {
        tags: ['Service Info'],
        description: 'Service root endpoint',
        response: {
          200: {
            type: 'object',
            properties: {
              service: { type: 'string' },
              status: { type: 'string' }
            }
          }
        }
      }
    }, async () => ({ service: "${SERVICE_NAME}", status: "running" }));
    
    await app.register(healthRoutes, { prefix: '/health' });

    app.log.info('Routes registered successfully');
  } catch (err) {
    app.log.error('Error registering routes:', err);
    throw err;
  }
};
EOF

cat >${SERVICE_NAME}/src/routes/health.ts <<EOF
import { FastifyInstance } from 'fastify';

export async function healthRoutes(app: FastifyInstance) {
  app.get('/live', {
    schema: {
      tags: ['Health'],
      description: 'Liveness probe',
      response: {
        200: {
          type: 'object',
          properties: {
            status: { type: 'string' }
          }
        }
      }
    }
  }, async () => ({ status: 'OK' }));

  app.get('/ready', {
    schema: {
      tags: ['Health'],
      description: 'Readiness probe',
      response: {
        200: {
          type: 'object',
          properties: {
            db: { type: 'string' }
          }
        }
      }
    }
  }, async () => ({ db: 'OK' }));
}
EOF

# Initialize Git
if command -v git &>/dev/null; then
  echo "Initializing Git repository..."
  cd ${SERVICE_NAME}
  git init
  git add .
  git commit -m "Initial commit for ${SERVICE_NAME} service"
  cd ..
else
  echo "Git not found. Skipping repository initialization."
fi

echo "✅ ${SERVICE_NAME} service created"
echo "Next steps:"
echo "1. cd ${SERVICE_NAME}"
echo "2. bun install"
echo "3. Create .env file with required environment variables:"
echo "   - JWT_JWKS_URI=your_auth_service_jwks_url"
echo "   - JWT_ISSUER=your_issuer"
echo "   - JWT_AUDIENCE=your_audience"
echo "   - DATABASE_URL=postgres://user:pass@host:port/db"
echo "4. Add service-specific routes and business logic"
echo "5. Access API docs at http://localhost:3000/docs"
