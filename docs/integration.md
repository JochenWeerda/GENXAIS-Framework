# Integration Guide

Guide for integrating GENXAIS Framework with various development tools and environments.

## Cursor.ai Integration

### Setup

1. Import SDK in Cursor.ai:
   ```python
   from genxais_sdk import GENXAISFramework
   ```

2. Initialize Framework:
   ```python
   framework = GENXAISFramework()
   framework.set_mode("VAN")  # Start in analysis mode
   ```

3. Configure Cursor.ai Settings:
   - Enable GENXAIS completion
   - Set mode-specific suggestions
   - Configure auto-transitions

### Command Palette Integration

Add GENXAIS commands to Cursor.ai palette:

```json
{
  "commands": {
    "genxais.analyze": {
      "title": "GENXAIS: Analyze Code",
      "command": "framework.analyze_current_file"
    },
    "genxais.generate": {
      "title": "GENXAIS: Generate Code",
      "command": "framework.generate_code"
    }
  }
}
```

### Keyboard Shortcuts

Configure mode-specific shortcuts:

```json
{
  "keybindings": {
    "ctrl+shift+v": "genxais.van_mode",
    "ctrl+shift+p": "genxais.plan_mode",
    "ctrl+shift+c": "genxais.create_mode",
    "ctrl+shift+i": "genxais.implement_mode"
  }
}
```

## IDE Integration

### VSCode Extension

1. Install GENXAIS VSCode Extension
2. Configure settings:
   ```json
   {
     "genxais.autoMode": true,
     "genxais.suggestions": true,
     "genxais.metrics": true
   }
   ```

### JetBrains Plugin

1. Install GENXAIS Plugin
2. Configure in Settings > Tools > GENXAIS
3. Enable auto-sync with framework modes

## CI/CD Integration

### GitHub Actions

```yaml
name: GENXAIS CI
on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: GENXAIS Analysis
        uses: genxais/github-action@v1
        with:
          mode: VAN
          metrics: true
```

### GitLab CI

```yaml
genxais_analysis:
  image: genxais/ci-image:latest
  script:
    - genxais-cli analyze
    - genxais-cli validate
```

## MongoDB Integration

### Connection Setup

```python
from genxais_sdk.storage import MongoDBConnector

connector = MongoDBConnector(
    uri="mongodb://localhost:27017",
    database="genxais_db"
)
```

### Collection Management

```python
# Initialize collections
connector.init_collections([
    "documents",
    "embeddings",
    "metadata"
])

# Verify indexes
connector.verify_indexes()
```

## RAG System Integration

### Storage Configuration

```python
from genxais_sdk.rag import RAGStorage

storage = RAGStorage(
    base_path="./rag_storage",
    mongodb_uri="mongodb://localhost:27017"
)

# Initialize storage
storage.initialize()
```

### Document Processing

```python
from genxais_sdk.rag import DocumentProcessor

processor = DocumentProcessor()
processor.process_document("path/to/doc.md")
```

## APM Framework Integration

### Cycle Management

```python
from genxais_sdk.apm import APMManager

apm = APMManager()
apm.start_cycle("VAN")
```

### Metrics Collection

```python
from genxais_sdk.apm import MetricsCollector

collector = MetricsCollector()
collector.collect_metrics()
```

## Error Handling Integration

### Global Error Handler

```python
from genxais_sdk.error_handling import ErrorHandler

handler = ErrorHandler()
handler.register_global_handler()
```

### Custom Error Strategies

```python
@handler.recovery_strategy("api_error")
def handle_api_error(error):
    # Custom recovery logic
    pass
```

## Event System Integration

### Event Subscription

```python
from genxais_sdk.events import EventSystem

events = EventSystem()

@events.on("mode_change")
def handle_mode_change(old_mode, new_mode):
    print(f"Mode changed: {old_mode} -> {new_mode}")
```

### Custom Events

```python
# Define custom event
events.define_event("custom_action")

# Emit event
events.emit("custom_action", {"data": "value"})
```

## Memory Bank Integration

### Context Management

```python
from genxais_sdk.memory import MemoryBank

memory = MemoryBank()
memory.store_context({"key": "value"})
```

### History Tracking

```python
# Track action
memory.track_action("code_generation", {
    "file": "example.py",
    "type": "function"
})

# Retrieve history
history = memory.get_history()
```

## Security Integration

### Authentication

```python
from genxais_sdk.security import SecurityManager

security = SecurityManager()
security.configure_auth(
    auth_type="oauth2",
    credentials_path="auth_config.json"
)
```

### Access Control

```python
@security.require_permission("write")
def protected_function():
    pass
```

## Monitoring Integration

### Metrics Export

```python
from genxais_sdk.monitoring import MetricsExporter

exporter = MetricsExporter()
exporter.configure_prometheus()
```

### Health Checks

```python
from genxais_sdk.monitoring import HealthCheck

health = HealthCheck()
health.add_check("mongodb", check_mongodb)
```

## Troubleshooting

### Common Integration Issues

1. MongoDB Connection
```python
try:
    connector.connect()
except ConnectionError:
    connector.fallback_to_local()
```

2. Mode Synchronization
```python
# Force mode sync
framework.sync_mode()
```

3. Event System
```python
# Debug event system
events.enable_debug()
```

## Best Practices

1. **Error Handling**
   - Implement global error handlers
   - Use mode-specific error strategies
   - Log all integration errors

2. **Performance**
   - Enable caching where appropriate
   - Use bulk operations for MongoDB
   - Implement connection pooling

3. **Security**
   - Follow least privilege principle
   - Encrypt sensitive data
   - Regular security audits

4. **Monitoring**
   - Set up comprehensive metrics
   - Configure alerting
   - Regular health checks 