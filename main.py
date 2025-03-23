#!/usr/bin/env python3
"""
Microservice Generator

A tool to scaffold new microservices for the Fairytale Realm platform
following the established architectural patterns.
"""

import argparse
import os
import sys
from pathlib import Path

from generator import MicroserviceGenerator


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a new microservice with the Fairytale Realm architecture"
    )
    parser.add_argument("service_name", help="Name of the microservice to generate")
    
    # Optional arguments
    parser.add_argument(
        "--output-dir", 
        "-o", 
        default=".", 
        help="Directory where the microservice should be created (default: current directory)"
    )
    parser.add_argument(
        "--skip-git", 
        action="store_true", 
        help="Skip git repository initialization"
    )
    parser.add_argument(
        "--verbose", 
        "-v", 
        action="store_true", 
        help="Enable verbose output"
    )
    
    return parser.parse_args()


def main():
    """Main entry point for the microservice generator."""
    args = parse_args()
    
    # Validate service name (no spaces, valid directory name)
    if not args.service_name.isalnum() and not all(c.isalnum() or c == '-' for c in args.service_name):
        print(f"Error: Service name '{args.service_name}' contains invalid characters")
        print("Service name should only contain alphanumeric characters and hyphens")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_path = Path(args.output_dir).resolve()
    if not output_path.exists():
        if args.verbose:
            print(f"Creating output directory: {output_path}")
        os.makedirs(output_path, exist_ok=True)
    
    # Initialize the generator
    generator = MicroserviceGenerator(
        service_name=args.service_name,
        output_dir=output_path,
        skip_git=args.skip_git,
        verbose=args.verbose
    )
    
    # Generate the microservice
    try:
        generator.generate()
        print(f"✅ {args.service_name} service created successfully")
        # Print next steps guide
        generator.print_next_steps()
    except Exception as e:
        print(f"❌ Error generating microservice: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 