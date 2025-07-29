"""
Direct Bedrock API utilities for vision models.

This module provides direct Bedrock API calls for models that don't work
well with PydanticAI's BinaryContent abstraction (like Nova models).
"""

import base64
import json

import boto3

from config.settings import AgentConfig


async def analyze_image_with_bedrock(
    image_bytes: bytes,
    prompt: str,
    config: AgentConfig,
    max_tokens: int = 1000,
    temperature: float = 0.3,
) -> str:
    """
    Analyze an image using direct Bedrock API call.

    Args:
        image_bytes: Raw image bytes (JPEG format) from screenshot tools
        prompt: Text prompt for analysis
        config: Agent configuration with model from .env
        max_tokens: Maximum tokens for response (default 1000)
        temperature: Temperature for response generation (default 0.3)

    Returns:
        Text response from the model

    Raises:
        Exception: If Bedrock API call fails or image analysis encounters errors
    """
    # Encode to base64 as required by the payload format
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    # Official AWS Bedrock Nova format from AWS documentation
    payload = {
        "schemaVersion": "messages-v1",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": "jpeg",
                            "source": {"bytes": base64_image},  # Base64 string for Invoke API
                        }
                    },
                    {"text": prompt},
                ],
            }
        ],
        "inferenceConfig": {"maxTokens": max_tokens, "temperature": temperature},
    }

    # Create Bedrock client with AWS credentials from config/.env
    client = boto3.client("bedrock-runtime", region_name=config.aws_region or "us-east-1")

    try:
        print(f"Calling Bedrock API with model: {config.llm_choice}")

        # Call Bedrock API directly using model from config.llm_choice (.env)
        response = client.invoke_model(
            modelId=config.llm_choice, body=json.dumps(payload)  # Gets from LLM_CHOICE in .env
        )

        # Parse Nova response format (different from Claude)
        response_body = json.loads(response["body"].read())
        analysis_text = response_body["output"]["message"]["content"][0]["text"]

        print(f"Bedrock analysis completed successfully ({len(analysis_text)} characters)")
        return analysis_text

    except Exception as e:
        error_msg = f"Error analyzing image with Bedrock: {str(e)}"
        print(f"Bedrock API error: {error_msg}")
        return error_msg


def should_use_bedrock_direct(config: AgentConfig) -> bool:
    """
    Check if we should use direct Bedrock API instead of PydanticAI.

    Args:
        config: Agent configuration (loads from .env)

    Returns:
        True if should use direct API, False to use PydanticAI
    """
    model_name = config.llm_choice.lower()  # From LLM_CHOICE in .env
    provider = config.llm_provider.lower()  # From LLM_PROVIDER in .env

    # Use direct API for Nova models on AWS
    return provider == "aws" and "nova" in model_name


async def analyze_full_screenshot_with_bedrock(
    image_bytes: bytes, config: AgentConfig, custom_prompt: str | None = None
) -> str:
    """
    Analyze a full screenshot with Bedrock API.

    Args:
        image_bytes: Raw image bytes from screenshot
        config: Agent configuration
        custom_prompt: Optional custom prompt, uses default if None

    Returns:
        Text analysis of the screenshot
    """
    prompt = (
        custom_prompt
        or "Please analyze this screenshot and describe what you see on the screen in detail."
    )
    return await analyze_image_with_bedrock(image_bytes, prompt, config)


async def analyze_region_screenshot_with_bedrock(
    image_bytes: bytes,
    x: int,
    y: int,
    width: int,
    height: int,
    config: AgentConfig,
    custom_prompt: str | None = None,
) -> str:
    """
    Analyze a region screenshot with Bedrock API.

    Args:
        image_bytes: Raw image bytes from region screenshot
        x: Left coordinate of the region
        y: Top coordinate of the region
        width: Width of the region
        height: Height of the region
        config: Agent configuration
        custom_prompt: Optional custom prompt, uses default if None

    Returns:
        Text analysis of the screenshot region
    """
    prompt = (
        custom_prompt
        or f"Please analyze this screenshot of a specific screen region (coordinates: x={x}, y={y}, width={width}, height={height}) and describe what you see in detail."
    )
    return await analyze_image_with_bedrock(image_bytes, prompt, config)


def test_bedrock_config(config: AgentConfig) -> str:
    """
    Test if Bedrock configuration is valid for vision analysis.

    Args:
        config: Agent configuration

    Returns:
        Status message about configuration
    """
    if not should_use_bedrock_direct(config):
        return f"Bedrock direct API not needed - Provider: {config.llm_provider}, Model: {config.llm_choice}"

    try:
        import boto3

        # Test if we can create the client (basic credential check)
        boto3.client("bedrock-runtime", region_name=config.aws_region or "us-east-1")

        return f"Bedrock configuration valid - Model: {config.llm_choice}, Region: {config.aws_region or 'us-east-1'}"

    except Exception as e:
        return f"Bedrock configuration error: {str(e)}"
