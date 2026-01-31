#!/bin/bash
# Quick setup script for schema-sentinel project

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== SQL Comparison Environment Setup ===${NC}\n"

# Ensure uv is in PATH
export PATH="$HOME/.local/bin:$HOME/.var/app/com.visualstudio.code/bin:$PATH"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo -e "${GREEN}✓${NC} uv is installed ($(uv --version))\n"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
    echo -e "${GREEN}✓${NC} Virtual environment created\n"
else
    echo -e "${GREEN}✓${NC} Virtual environment already exists\n"
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
uv pip install -e ".[dev,jupyter]"

echo -e "\n${GREEN}=== Setup Complete! ===${NC}"
echo -e "\nTo activate the environment in the future, run:"
echo -e "  ${BLUE}source .venv/bin/activate${NC}"
echo -e "\nOr use the Makefile:"
echo -e "  ${BLUE}make help${NC} - Show available commands"
