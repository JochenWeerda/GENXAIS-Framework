# API Reference

Complete API documentation for the GENXAIS Framework.

## Core Framework

### GENXAISFramework

Main framework class that provides access to all GENXAIS features.

```python
from genxais_sdk import GENXAISFramework

framework = GENXAISFramework(config_path: Optional[str] = None)
```

#### Methods

##### `set_mode(mode: str) -> bool`
Set the current development mode.

Parameters:
- `mode`: One of "VAN", "PLAN", "CREATE", "IMPLEMENT", "REFLECT", "ARCHIVE"

Returns:
- `bool`: Success status

##### `get_mode() -> str`
Get the current development mode.

Returns:
- `str`: Current mode

## RAG System

### RAGStorageInitializer

Initialize and manage RAG storage components.

```python
from rag_system.init_storage import RAGStorageInitializer

initializer = RAGStorageInitializer(mongodb_uri: Optional[str] = None)
```

#### Methods

##### `init_filesystem() -> Dict[str, Any]`
Initialize filesystem structure.

Returns:
- Dictionary with initialization status

##### `init_mongodb() -> Dict[str, Any]`
Initialize MongoDB collections and indexes.

Returns:
- Dictionary with initialization status

##### `initialize_all() -> Dict[str, Any]`
Initialize all RAG components.

Returns:
- Dictionary with complete initialization status

## Error Handling

### SDKErrorHandler

Manage and recover from errors.

```python
from error_handling import SDKErrorHandler

handler = SDKErrorHandler()
```

#### Methods

##### `handle_error(error_type: str, error_details: Dict[str, Any], context: str = "") -> Dict[str, Any]`
Handle specific error types with recovery strategies.

Parameters:
- `error_type`: Type of error
- `error_details`: Error details
- `context`: Error context

Returns:
- Dictionary with error handling results

##### `safe_execute(func: Callable, *args, **kwargs) -> Dict[str, Any]`
Safely execute a function with error handling.

Parameters:
- `func`: Function to execute
- `*args`: Positional arguments
- `**kwargs`: Keyword arguments

Returns:
- Dictionary with execution results

## APM Framework

### APMCycleManager

Manage APM development cycles.

```python
from apm_framework import APMCycleManager

manager = APMCycleManager()
```

#### Methods

##### `start_cycle(mode: str) -> Dict[str, Any]`
Start a new APM cycle.

Parameters:
- `mode`: Development mode

Returns:
- Dictionary with cycle status

##### `end_cycle() -> Dict[str, Any]`
End current APM cycle.

Returns:
- Dictionary with cycle results

## Agent System

### BaseAgent

Base class for all agents.

```python
from agents import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__()
```

#### Methods

##### `validate_action(action: str, context: Dict[str, Any]) -> bool`
Validate if action is allowed in current mode.

Parameters:
- `action`: Proposed action
- `context`: Action context

Returns:
- `bool`: Action validity

## Memory Bank

### MemoryManager

Manage development context and history.

```python
from memory_bank import MemoryManager

memory = MemoryManager()
```

#### Methods

##### `store_context(context: Dict[str, Any]) -> str`
Store development context.

Parameters:
- `context`: Context data

Returns:
- `str`: Context ID

##### `retrieve_context(context_id: str) -> Dict[str, Any]`
Retrieve stored context.

Parameters:
- `context_id`: Context identifier

Returns:
- Dictionary with context data

## Utility Functions

### Token Optimization

```python
from genxais_sdk.utils import optimize_tokens

optimized = optimize_tokens(text: str, max_tokens: int) -> str
```

### Pipeline Management

```python
from genxais_sdk.utils import create_pipeline

pipeline = create_pipeline(steps: List[Dict[str, Any]]) -> Pipeline
```

## Event System

### EventEmitter

```python
from genxais_sdk.events import EventEmitter

emitter = EventEmitter()
emitter.on("event_name", callback_function)
emitter.emit("event_name", event_data)
```

## Configuration

### ConfigManager

```python
from genxais_sdk.config import ConfigManager

config = ConfigManager()
config.load_config("config.json")
config.get_value("key")
config.set_value("key", "value")
```

## Constants

```python
from genxais_sdk.constants import *

MODES = ["VAN", "PLAN", "CREATE", "IMPLEMENT", "REFLECT", "ARCHIVE"]
DEFAULT_TIMEOUT = 60
MAX_RETRIES = 3
```

## Type Definitions

```python
from genxais_sdk.types import *

Pipeline = List[Dict[str, Any]]
Context = Dict[str, Any]
ActionResult = Dict[str, Any]
``` 