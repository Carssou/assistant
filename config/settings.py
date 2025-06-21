"""
Configuration management using Pydantic models.

This module provides configuration classes for the PydanticAI agent,
mapping directly to environment variables defined in .env.example.
"""

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    
    AWS = "aws"
    OPENAI = "openai"


class AgentConfig(BaseSettings):
    """Main agent configuration using Pydantic Settings."""
    
    # LLM Configuration
    llm_provider: LLMProvider = Field(default=LLMProvider.AWS, description="LLM provider to use")
    llm_base_url: Optional[str] = Field(default=None, description="Base URL for custom endpoints")
    llm_api_key: Optional[str] = Field(default=None, description="API key for the LLM provider")
    llm_choice: str = Field(default="claude-3-5-sonnet", description="Model choice")
    
    # AWS Bedrock Configuration
    aws_region: str = Field(default="us-east-1", description="AWS region for Bedrock")
    aws_access_key_id: Optional[str] = Field(default=None, description="AWS access key ID")
    aws_secret_access_key: Optional[str] = Field(default=None, description="AWS secret access key")
    
    # Obsidian MCP Server Configuration
    obsidian_vault_path: Optional[Path] = Field(default=None, description="Path to Obsidian vault")
    obsidian_daily_notes_path: str = Field(default="Daily Notes", description="Daily notes subfolder")
    obsidian_templates_path: str = Field(default="Templates", description="Templates subfolder")
    
    # SearXNG MCP Server Configuration
    searxng_base_url: str = Field(default="http://localhost:8080", description="SearXNG instance URL")
    searxng_api_key: Optional[str] = Field(default=None, description="SearXNG API key if required")
    
    # Todoist MCP Server Configuration
    todoist_api_token: Optional[str] = Field(default=None, description="Todoist API token")
    todoist_project_id: Optional[str] = Field(default=None, description="Default project ID")
    
    # YouTube MCP Server Configuration
    youtube_api_key: Optional[str] = Field(default=None, description="YouTube API key")
    youtube_transcript_language: str = Field(default="en", description="Default transcript language")
    
    # Development & Monitoring
    log_level: str = Field(default="INFO", description="Logging level")
    langfuse_secret_key: Optional[str] = Field(default=None, description="Langfuse secret key")
    langfuse_public_key: Optional[str] = Field(default=None, description="Langfuse public key")
    langfuse_host: str = Field(default="https://cloud.langfuse.com", description="Langfuse host")
    debug_mode: bool = Field(default=False, description="Enable debug mode")
    
    # GUI Configuration
    gui_theme: str = Field(default="default", description="Gradio theme")
    gui_port: int = Field(default=7860, description="GUI port")
    gui_share: bool = Field(default=False, description="Enable public sharing")
    
    @field_validator("obsidian_vault_path")
    @classmethod
    def validate_vault_path(cls, v):
        """Validate that the vault path exists if provided."""
        if v is not None:
            # Skip validation for placeholder paths
            if str(v) == "/path/to/your/vault":
                return None
            if not v.exists():
                raise ValueError(f"Obsidian vault path does not exist: {v}")
            if not v.is_dir():
                raise ValueError(f"Obsidian vault path is not a directory: {v}")
        return v
    
    @field_validator("debug_mode", mode="before")
    @classmethod
    def parse_debug_mode(cls, v):
        """Parse debug mode from string if needed."""
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return v
    
    @field_validator("gui_share", mode="before")
    @classmethod
    def parse_gui_share(cls, v):
        """Parse GUI share from string if needed."""
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return v
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }


def create_model_instance(config: AgentConfig):
    """
    Create a PydanticAI model instance based on configuration.
    
    Args:
        config: Agent configuration
        
    Returns:
        PydanticAI model instance
    """
    if config.llm_provider == LLMProvider.AWS:
        # Set AWS environment variables for the AWS SDK to use
        import os
        if config.aws_access_key_id:
            os.environ['AWS_ACCESS_KEY_ID'] = config.aws_access_key_id
        if config.aws_secret_access_key:
            os.environ['AWS_SECRET_ACCESS_KEY'] = config.aws_secret_access_key
        if config.aws_region:
            os.environ['AWS_DEFAULT_REGION'] = config.aws_region
            
        from pydantic_ai.models.bedrock import BedrockConverseModel
        return BedrockConverseModel(model_name=config.llm_choice)
            
    elif config.llm_provider == LLMProvider.OPENAI:
        from pydantic_ai.models.openai import OpenAIModel
        return OpenAIModel(
            model_name=config.llm_choice,
            api_key=config.llm_api_key,
            base_url=config.llm_base_url
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {config.llm_provider}")


def get_model_string(config: AgentConfig) -> str:
    """
    Get the model string for PydanticAI based on configuration.
    
    Args:
        config: Agent configuration
        
    Returns:
        Model string for PydanticAI
    """
    if config.llm_provider == LLMProvider.AWS:
        return f"bedrock:{config.llm_choice}"
    elif config.llm_provider == LLMProvider.OPENAI:
        return f"openai:{config.llm_choice}"
    else:
        raise ValueError(f"Unsupported LLM provider: {config.llm_provider}")


def load_config() -> AgentConfig:
    """
    Load configuration from environment variables and .env file.
    
    Returns:
        Loaded agent configuration
    """
    return AgentConfig()