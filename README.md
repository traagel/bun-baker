# Microservice Generator

A tool to scaffold new microservices for the Fairytale Realm platform following the established architectural patterns.

## Features

- Creates a complete TypeScript microservice structure with Fastify
- Includes JWT authentication, Swagger documentation, and error handling
- Sets up a PostgreSQL database connection
- Configures environment variables and logging
- Creates a Dockerfile for containerization
- Initializes a Git repository (optional)

## Requirements

- Python 3.6 or higher
- Optional: Jinja2 for advanced template rendering (`pip install jinja2`)
- Optional: Git for repository initialization

## Installation

Clone this repository or copy the files to your project:

```bash
git clone <repository-url>
cd <repository-directory>
```

## Usage

```bash
python generate_microservices/main.py <service-name> [options]
```

### Arguments

- `service_name`: The name of the microservice to generate (required)

### Options

- `--output-dir`, `-o`: Directory where the microservice should be created (default: current directory)
- `--skip-git`: Skip Git repository initialization
- `--verbose`, `-v`: Enable verbose output

### Examples

```bash
# Generate a users service in the current directory
python generate_microservices/main.py users

# Generate a payments service in a specific directory with verbose output
python generate_microservices/main.py payments -o ./services -v

# Generate a notifications service without Git initialization
python generate_microservices/main.py notifications --skip-git
```

## Directory Structure

The generated microservice will have the following structure:

```
service-name/
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── src/
│   ├── data-access/       # Database access layer
│   ├── db/
│   │   └── migrations/    # Database migrations
│   ├── models/            # Data models
│   ├── plugins/           # Fastify plugins
│   ├── routes/            # API routes
│   ├── schemas/           # Request/response schemas
│   └── utils/             # Utility functions
├── .gitignore
├── Dockerfile
├── package.json
└── tsconfig.json
```

## Customizing Templates

You can customize the generated files by modifying the templates in the `generate_microservices/templates/` directory. All templates use Jinja2 syntax with variables like `{{ service_name }}`.

Available variables:
- `service_name`: The provided service name
- `service_name_uppercase`: The service name in uppercase
- `service_name_capitalized`: The service name with the first letter capitalized

## License

MIT 