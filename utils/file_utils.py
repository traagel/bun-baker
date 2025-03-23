"""
File utilities for the microservice generator.

This module provides functions for working with files and directories,
including template rendering and file system operations.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

# Jinja2 is used for template rendering
try:
    from jinja2 import Environment, FileSystemLoader, Template
    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False


def ensure_directory(directory_path: Path) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: The path to the directory to ensure exists
    """
    directory_path.mkdir(parents=True, exist_ok=True)


def write_file(file_path: Path, content: str) -> None:
    """
    Write content to a file, creating parent directories if needed.
    
    Args:
        file_path: The path to the file to write
        content: The content to write to the file
    """
    # Ensure the directory exists
    ensure_directory(file_path.parent)
    
    # Write the content to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def render_template(template_path: Path, variables: Dict[str, Any]) -> str:
    """
    Render a template with the given variables.
    
    Args:
        template_path: Path to the template file
        variables: Dictionary of variables to use in the template
        
    Returns:
        The rendered template as a string
        
    Raises:
        FileNotFoundError: If the template file does not exist
        ImportError: If Jinja2 is not installed
        Exception: If there is an error rendering the template
    """
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    
    if HAS_JINJA2:
        # Use Jinja2 for template rendering if available
        env = Environment(
            loader=FileSystemLoader(str(template_path.parent)),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        template = env.get_template(template_path.name)
        return template.render(**variables)
    else:
        # Fallback to basic string replacement if Jinja2 is not available
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Replace placeholders in the form {{variable_name}}
        for key, value in variables.items():
            content = content.replace('{{' + key + '}}', str(value))
            
        return content


def copy_file(source_path: Path, destination_path: Path) -> None:
    """
    Copy a file from source to destination, creating parent directories if needed.
    
    Args:
        source_path: The path to the source file
        destination_path: The path to the destination file
    
    Raises:
        FileNotFoundError: If the source file does not exist
    """
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")
    
    # Ensure the destination directory exists
    ensure_directory(destination_path.parent)
    
    # Copy the file
    with open(source_path, 'rb') as src, open(destination_path, 'wb') as dst:
        dst.write(src.read()) 