#!/bin/bash
# CI test script to run tests in a clean environment

# Clear potentially problematic environment variables
unset LLM_PROVIDER LLM_CHOICE LLM_API_KEY DISPLAY

# Create test directories for CI environment
mkdir -p /tmp/test-vault
mkdir -p /tmp/test-vault/Daily\ Notes
mkdir -p /tmp/test-vault/Templates

# Set minimal environment variables for tests
export OBSIDIAN_VAULT_PATH="/tmp/test-vault"
export OBSIDIAN_DAILY_NOTES_PATH="Daily Notes"
export OBSIDIAN_TEMPLATES_PATH="Templates"
export LLM_PROVIDER="aws"
export LLM_CHOICE="amazon.nova-lite-v1:0"
export AWS_REGION="us-east-1"

# Run tests with clean environment
python -m pytest tests/ -v --tb=short