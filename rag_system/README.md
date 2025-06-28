# RAG System

The RAG (Retrieval-Augmented Generation) system provides document storage, embedding management, and retrieval capabilities for the GENXAIS Framework.

## Components

- Document Storage
- Embedding Management
- Chunking System
- MongoDB Integration
- Error Handling

## Storage Structure

```
rag_system/
├── storage/
│   ├── documents/     # Raw document storage
│   ├── embeddings/    # Document embeddings
│   ├── backup/        # Backup storage
│   ├── indexes/       # Search indexes
│   ├── temp/         # Temporary files
│   └── error_logs/   # Error logging
├── init_storage.py   # Storage initialization
└── rag_service.py    # Main RAG service
```

## MongoDB Collections

- `documents`: Document storage with metadata
- `embeddings`: Vector embeddings for documents
- `chunks`: Document chunks for processing
- `metadata`: System metadata
- `indexes`: Search indexes
- `error_logs`: Error tracking

## Initialization

To initialize the RAG system:

```bash
# Set MongoDB URI if not using default
export MONGODB_URI="mongodb://your-server:27017"

# Run initialization
python init_storage.py
```

## Collection Schemas

### Documents
```json
{
    "title": "string",
    "content": "string",
    "created_at": "date",
    "updated_at": "date",
    "metadata": "object"
}
```

### Embeddings
```json
{
    "doc_id": "objectId",
    "embedding": "array",
    "created_at": "date"
}
```

### Chunks
```json
{
    "doc_id": "objectId",
    "content": "string",
    "position": "int",
    "metadata": "object"
}
```

## Error Handling

The system includes comprehensive error handling:
- Filesystem errors
- MongoDB connection issues
- Data validation errors
- Storage management errors

## Integration

The RAG system integrates with:
- Error Handling Framework
- APM Framework
- Memory Bank
- Document Processing Pipeline 