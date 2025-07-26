#!/bin/bash
# CI test script to run tests in a clean environment

# Clear potentially problematic environment variables
unset LLM_PROVIDER LLM_CHOICE LLM_API_KEY DISPLAY

# Set minimal environment variables for tests (no Obsidian vault path to avoid validation)
export LLM_PROVIDER="aws"
export LLM_CHOICE="amazon.nova-lite-v1:0"
export AWS_REGION="us-east-1"

# Run tests with clean environment
python -m pytest tests/ -v --tb=short