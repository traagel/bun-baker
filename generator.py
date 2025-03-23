"""
Microservice Generator

Core generator logic for scaffolding new microservices.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from utils.file_utils import render_template, ensure_directory, write_file


class MicroserviceGenerator:
    """Generator for creating new microservices from templates."""

    def __init__(
        self,
        service_name: str,
        output_dir: Path,
        skip_git: bool = False,
        verbose: bool = False
    ):
        self.service_name = service_name
        self.output_dir = output_dir
        self.skip_git = skip_git
        self.verbose = verbose
        
        # Compute paths
        self.service_dir = output_dir / service_name
        self.template_dir = Path(__file__).parent / "templates"
        
        # Template variables
        self.vars = {
            "service_name": service_name,
            "service_name_uppercase": service_name.upper(),
            "service_name_capitalized": service_name.capitalize(),
        }
        
        if self.verbose:
            print(f"Service name: {service_name}")
            print(f"Output directory: {output_dir}")
            print(f"Service directory: {self.service_dir}")
            print(f"Template directory: {self.template_dir}")

    def generate(self):
        """Generate the full microservice structure."""
        self._create_directory_structure()
        self._generate_files()
        
        if not self.skip_git:
            self._initialize_git()

    def _create_directory_structure(self):
        """Create the directory structure for the microservice."""
        if self.verbose:
            print("Creating directory structure...")
            
        # Main directories
        dirs = [
            "src/data-access",
            "src/models",
            "src/routes",
            "src/schemas",
            "src/utils",
            "src/db/migrations",
            "src/plugins",
            "docs",
            "scripts"
        ]
        
        for dir_path in dirs:
            full_path = self.service_dir / dir_path
            ensure_directory(full_path)
            if self.verbose:
                print(f"Created directory: {full_path}")

    def _generate_files(self):
        """Generate all the required files from templates."""
        if self.verbose:
            print("Generating files from templates...")
            
        # Root files
        self._generate_file(".gitignore", "gitignore.tmpl")
        self._generate_file("tsconfig.json", "tsconfig.json.tmpl")
        self._generate_file("package.json", "package.json.tmpl")
        self._generate_file("Dockerfile", "Dockerfile.tmpl")
        self._generate_file(".env.example", "env.example.tmpl")
        
        # Source files
        self._generate_file("src/app.ts", "app.ts.tmpl")
        self._generate_file("src/config.ts", "config.ts.tmpl")
        self._generate_file("src/utils/errorHandler.ts", "errorHandler.ts.tmpl")
        self._generate_file("src/utils/sanitizer.ts", "sanitizer.ts.tmpl")
        self._generate_file("src/plugins/index.ts", "plugins.ts.tmpl")
        self._generate_file("src/routes/index.ts", "routes-index.ts.tmpl")
        self._generate_file("src/routes/health.ts", "health-routes.ts.tmpl")
        
        # DB Migration files
        self._generate_file("src/db/migrate.ts", "migrate.ts.tmpl")
        self._generate_file("src/db/migrations/001_initial_schema.sql", "001_initial_schema.sql.tmpl")
        
        # Create a simple README for the service
        self._generate_readme()
    
    def _generate_file(self, relative_path: str, template_name: str):
        """Generate a single file from a template."""
        target_path = self.service_dir / relative_path
        template_path = self.template_dir / template_name
        
        # Ensure the directory exists
        ensure_directory(target_path.parent)
        
        try:
            # Render the template and write to the target path
            content = render_template(template_path, self.vars)
            write_file(target_path, content)
            
            if self.verbose:
                print(f"Generated file: {target_path}")
        except Exception as e:
            print(f"Error generating file {target_path}: {e}")
            raise
    
    def _generate_readme(self):
        """Generate a README.md file for the service."""
        content = f"""# {self.service_name.capitalize()} Service

A microservice for the Fairytale Realm platform that handles {self.service_name} functionality.

## Features

- RESTful API with Fastify
- JWT authentication
- PostgreSQL database
- Swagger documentation
- Containerized with Docker

## Development

### Prerequisites

- Node.js >= 20.0.0
- Bun >= 0.6.0
- PostgreSQL

### Getting Started

1. Install dependencies:
   ```bash
   bun install
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Run database migrations:
   ```bash
   bun run migrate
   ```

4. Start the development server:
   ```bash
   bun run dev
   ```

5. Access the API documentation at [http://localhost:3000/docs](http://localhost:3000/docs)

## API Routes

- `GET /health/live` - Liveness probe
- `GET /health/ready` - Readiness probe with database check

## Deployment

Build and deploy with Docker:

```bash
docker build -t {self.service_name}-service .
docker run -p 3000:3000 {self.service_name}-service
```
"""
        
        target_path = self.service_dir / "README.md"
        write_file(target_path, content)
        
        if self.verbose:
            print(f"Generated README: {target_path}")

    def _initialize_git(self):
        """Initialize a git repository if git is available."""
        try:
            # Check if git is available
            subprocess.run(
                ["git", "--version"], 
                check=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            
            if self.verbose:
                print("Initializing Git repository...")
                
            # Change directory to service directory
            cwd = os.getcwd()
            os.chdir(self.service_dir)
            
            try:
                # Initialize git repository
                subprocess.run(["git", "init"], check=True)
                subprocess.run(["git", "add", "."], check=True)
                subprocess.run(
                    ["git", "commit", "-m", f"Initial commit for {self.service_name} service"],
                    check=True
                )
                
                if self.verbose:
                    print("Git repository initialized successfully")
            finally:
                # Change back to original directory
                os.chdir(cwd)
        except subprocess.CalledProcessError:
            print("Git not found or error initializing repository. Skipping git initialization.")
        except Exception as e:
            print(f"Error initializing git repository: {e}")

    def print_next_steps(self):
        """Print the next steps for the user."""
        print("\nNext steps:")
        print(f"1. cd {self.service_name}")
        print("2. bun install")
        print("3. Create .env file with required environment variables:")
        print("   - JWT_JWKS_URI=your_auth_service_jwks_url")
        print("   - JWT_ISSUER=your_issuer")
        print("   - JWT_AUDIENCE=your_audience")
        print("   - DATABASE_URL=postgres://user:pass@host:port/db")
        print("4. Add service-specific routes and business logic")
        print("5. Access API docs at http://localhost:3000/docs") 