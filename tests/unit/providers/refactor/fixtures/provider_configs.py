"""Test configuration fixtures for provider testing."""

# OpenAI Provider Configurations
VALID_OPENAI_CONFIG = {
    "api_key": "sk-test123",
    "model": "dall-e-3",
    "size": "1024x1024",
    "rate_limit_delay": 1.0,
    "max_retries": 3,
    "timeout": 30,
}

MINIMAL_OPENAI_CONFIG = {"api_key": "sk-test456"}

INVALID_OPENAI_CONFIGS = {
    "missing_api_key": {"model": "dall-e-3"},
    "invalid_model": {"api_key": "sk-test123", "model": "invalid-model"},
    "invalid_size": {
        "api_key": "sk-test123",
        "model": "dall-e-3",
        "size": "invalid-size",
    },
    "negative_rate_limit": {"api_key": "sk-test123", "rate_limit_delay": -1.0},
    "invalid_max_retries": {"api_key": "sk-test123", "max_retries": -1},
}

# Forvo Provider Configurations
VALID_FORVO_CONFIG = {
    "api_key": "test_forvo_key",
    "country_priorities": ["US", "ES", "MX"],
    "format": "mp3",
    "rate_limit_delay": 0.5,
    "max_retries": 2,
}

MINIMAL_FORVO_CONFIG = {"api_key": "test_forvo_key_minimal"}

INVALID_FORVO_CONFIGS = {
    "missing_api_key": {"country_priorities": ["US", "ES"]},
    "invalid_country_code": {
        "api_key": "test_forvo_key",
        "country_priorities": ["INVALID"],
    },
    "invalid_format": {
        "api_key": "test_forvo_key",
        "format": "wav",  # Assuming only mp3 is supported
    },
    "empty_country_priorities": {"api_key": "test_forvo_key", "country_priorities": []},
}

# Runware Provider Configurations (for future use)
VALID_RUNWARE_CONFIG = {
    "api_key": "test_runware_key",
    "endpoint_url": "https://api.runware.ai/v1",
    "model": "stable-diffusion-v1-5",
    "rate_limit_delay": 2.0,
    "max_retries": 3,
}

INVALID_RUNWARE_CONFIGS = {
    "missing_api_key": {"endpoint_url": "https://api.runware.ai/v1"},
    "invalid_endpoint": {"api_key": "test_runware_key", "endpoint_url": "not-a-url"},
}

# Generic Provider Configuration Templates
BASE_PROVIDER_CONFIG = {"rate_limit_delay": 1.0, "max_retries": 3, "timeout": 30}

# Test Scenarios Configuration
TEST_SCENARIOS = {
    "rate_limiting": {
        "config": {
            "api_key": "test_rate_limit",
            "rate_limit_delay": 0.1,  # Fast for testing
            "max_retries": 2,
        },
        "expected_delays": [0.1, 0.2, 0.4],  # Exponential backoff
    },
    "api_failures": {
        "config": {"api_key": "test_failures", "max_retries": 3},
        "error_sequence": [
            {"status_code": 500, "retry": True},
            {"status_code": 429, "retry": True},
            {"status_code": 200, "retry": False},
        ],
    },
    "large_batch_processing": {
        "config": {"api_key": "test_batch", "batch_size": 5, "rate_limit_delay": 0.1},
        "test_data": {"batch_size": 50, "expected_batches": 10},
    },
}

# Configuration Validation Patterns
REQUIRED_FIELDS = {
    "openai": ["api_key"],
    "forvo": ["api_key"],
    "runware": ["api_key", "endpoint_url"],
}

OPTIONAL_FIELDS = {
    "openai": ["model", "size", "rate_limit_delay", "max_retries", "timeout"],
    "forvo": ["country_priorities", "format", "rate_limit_delay", "max_retries"],
    "runware": ["model", "rate_limit_delay", "max_retries", "timeout"],
}

DEFAULT_VALUES = {
    "openai": {
        "model": "dall-e-3",
        "size": "1024x1024",
        "rate_limit_delay": 1.0,
        "max_retries": 3,
        "timeout": 30,
    },
    "forvo": {
        "country_priorities": ["US", "GB"],
        "format": "mp3",
        "rate_limit_delay": 1.0,
        "max_retries": 3,
    },
    "runware": {
        "model": "stable-diffusion-v1-5",
        "rate_limit_delay": 2.0,
        "max_retries": 3,
        "timeout": 60,
    },
}
