#!/bin/bash
# CI test script to run tests in a clean environment

# Clear potentially problematic environment variables
unset LLM_PROVIDER LLM_CHOICE LLM_API_KEY DISPLAY

# Run tests with clean environment
python -m pytest tests/ -v --tb=short