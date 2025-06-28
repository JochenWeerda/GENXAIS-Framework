# Error Handling Framework

The Error Handling Framework provides robust error management and recovery strategies for the GENXAIS Framework.

## Features

- Comprehensive error logging and documentation
- Automatic recovery strategies for common errors
- Safe execution wrapper for critical functions
- API key management and recovery
- File system error handling
- Network error recovery
- APM cycle recovery
- RAG storage recovery
- Dependency management

## Usage

```python
from error_handling import SDKErrorHandler, safe_execute

# Initialize error handler
error_handler = SDKErrorHandler()

# Handle specific error
result = error_handler.handle_error(
    error_type="api_key_missing",
    error_details={"service": "openai"},
    context="API call"
)

# Safe execution wrapper
result = safe_execute(my_function, arg1, arg2, kwarg1="value")
```

## Directory Structure

```
error_handling/
├── __init__.py
├── framework.py
└── README.md
```

## Required Directories

The framework expects the following directory structure:

```
GENXAIS-Framework/
├── logs/
│   └── error_docs/
├── apm_framework/
│   └── last_state.json
└── rag_system/
    ├── storage/
    └── backup/
```

These directories are created automatically when needed.

## Integration

The Error Handling Framework is integrated with:
- APM Framework for cycle recovery
- RAG System for storage management
- Dependency management system
- Logging infrastructure

## Error Types

Supported error types:
- `api_key_missing`
- `file_not_found`
- `import_error`
- `permission_denied`
- `network_error`
- `apm_cycle_interrupted`
- `rag_storage_failed`
- `dependency_missing`

Each error type has its own recovery strategy implemented in the `SDKErrorHandler` class. 