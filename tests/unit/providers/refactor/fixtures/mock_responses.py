"""Mock API response fixtures for provider testing."""

# OpenAI API Response Fixtures
OPENAI_DALLE_SUCCESS_RESPONSE = {
    "data": [
        {
            "url": "https://oaidalleapiprodscus.blob.core.windows.net/test1.png",
            "revised_prompt": "A realistic photo of a red apple on a white background",
        },
        {
            "url": "https://oaidalleapiprodscus.blob.core.windows.net/test2.png",
            "revised_prompt": "A realistic photo of a red apple on a white background, different angle",
        },
    ]
}

OPENAI_DALLE_ERROR_RESPONSES = {
    "invalid_prompt": {
        "error": {
            "code": "invalid_prompt",
            "message": "The prompt contains content that violates our usage policies.",
            "type": "invalid_request_error",
        }
    },
    "rate_limit": {
        "error": {
            "code": "rate_limit_exceeded",
            "message": "Rate limit exceeded. Please try again later.",
            "type": "rate_limit_error",
        }
    },
    "insufficient_quota": {
        "error": {
            "code": "insufficient_quota",
            "message": "You exceeded your current quota, please check your plan and billing details.",
            "type": "insufficient_quota",
        }
    },
}

# Forvo API Response Fixtures
FORVO_SUCCESS_RESPONSE = {
    "attributes": {"total": 2},
    "items": [
        {
            "id": 12345,
            "word": "hola",
            "original": "hola",
            "addtime": "2023-01-15 10:30:00",
            "hits": 1500,
            "username": "spanish_native",
            "sex": "f",
            "country": "ES",
            "code": "es",
            "langname": "Spanish",
            "pathmp3": "https://api.forvo.com/audio/12345.mp3",
            "pathogv": "https://api.forvo.com/audio/12345.ogv",
            "rate": 5,
            "num_votes": 12,
            "num_positive_votes": 11,
        },
        {
            "id": 12346,
            "word": "hola",
            "original": "hola",
            "addtime": "2023-01-20 14:15:00",
            "hits": 800,
            "username": "mexico_user",
            "sex": "m",
            "country": "MX",
            "code": "es",
            "langname": "Spanish",
            "pathmp3": "https://api.forvo.com/audio/12346.mp3",
            "pathogv": "https://api.forvo.com/audio/12346.ogv",
            "rate": 4,
            "num_votes": 8,
            "num_positive_votes": 7,
        },
    ],
}

FORVO_NOT_FOUND_RESPONSE = {"attributes": {"total": 0}, "items": []}

FORVO_ERROR_RESPONSES = {
    "invalid_api_key": {"error": "Invalid API key"},
    "word_not_found": {"attributes": {"total": 0}, "items": []},
    "rate_limit": {"error": "Rate limit exceeded"},
    "service_unavailable": {"error": "Service temporarily unavailable"},
}

# Runware API Response Fixtures (for future use)
RUNWARE_SUCCESS_RESPONSE = {
    "status": "success",
    "data": {
        "task_id": "task_12345",
        "images": [
            {
                "url": "https://api.runware.ai/images/generated_12345.png",
                "width": 1024,
                "height": 1024,
                "format": "png",
            }
        ],
        "prompt": "A red apple on white background",
        "model": "stable-diffusion-v1-5",
        "steps": 30,
        "guidance_scale": 7.5,
    },
}

RUNWARE_ERROR_RESPONSES = {
    "invalid_prompt": {
        "status": "error",
        "error": {
            "code": "INVALID_PROMPT",
            "message": "The provided prompt contains invalid content",
        },
    },
    "quota_exceeded": {
        "status": "error",
        "error": {"code": "QUOTA_EXCEEDED", "message": "Monthly quota exceeded"},
    },
}

# HTTP Response Status Codes
HTTP_STATUS_CODES = {
    "success": 200,
    "bad_request": 400,
    "unauthorized": 401,
    "forbidden": 403,
    "not_found": 404,
    "rate_limit": 429,
    "server_error": 500,
    "service_unavailable": 503,
}

# Sample Audio Data (as bytes for testing)
SAMPLE_AUDIO_DATA = {
    "mp3_header": b"\xff\xfb\x90\x00",  # MP3 header bytes
    "small_mp3": b"\xff\xfb\x90\x00" + b"\x00" * 100,  # Minimal MP3 data
    "empty": b"",
    "invalid": b"INVALID_AUDIO_DATA",
}

# Sample Image URLs for testing
SAMPLE_IMAGE_URLS = [
    "https://oaidalleapiprodscus.blob.core.windows.net/test1.png",
    "https://oaidalleapiprodscus.blob.core.windows.net/test2.png",
    "https://api.runware.ai/images/generated_12345.png",
    "https://example.com/sample_image.jpg",
]

# Rate Limiting Response Headers
RATE_LIMIT_HEADERS = {
    "standard": {
        "X-RateLimit-Limit": "60",
        "X-RateLimit-Remaining": "0",
        "X-RateLimit-Reset": "1640995200",
        "Retry-After": "60",
    },
    "openai": {
        "x-ratelimit-limit-requests": "3000",
        "x-ratelimit-remaining-requests": "0",
        "x-ratelimit-reset-requests": "1s",
    },
}

# Test Scenarios Response Sequences
RESPONSE_SEQUENCES = {
    "retry_then_success": [
        {"status_code": 500, "response": {"error": "Internal server error"}},
        {"status_code": 429, "response": {"error": "Rate limit exceeded"}},
        {"status_code": 200, "response": OPENAI_DALLE_SUCCESS_RESPONSE},
    ],
    "progressive_failure": [
        {"status_code": 429, "response": {"error": "Rate limit exceeded"}},
        {"status_code": 500, "response": {"error": "Internal server error"}},
        {"status_code": 503, "response": {"error": "Service unavailable"}},
    ],
    "forvo_country_fallback": [
        {"country": "US", "response": FORVO_NOT_FOUND_RESPONSE},
        {"country": "ES", "response": FORVO_SUCCESS_RESPONSE},
        {"country": "MX", "response": FORVO_SUCCESS_RESPONSE},
    ],
}
