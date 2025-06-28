# Installation Guide

This guide will help you install and set up the GENXAIS Framework.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- MongoDB 4.4 or higher
- Git

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/GENXAIS-Framework.git
cd GENXAIS-Framework
```

### 2. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure MongoDB

1. Start MongoDB service
2. Set MongoDB URI in `.env`:
   ```
   MONGODB_URI=mongodb://localhost:27017
   ```

### 5. Initialize Framework

```bash
python -m genxais_sdk init
```

### 6. Verify Installation

```bash
python -m pytest
```

## Configuration

### Basic Configuration

Create `config.json` in your project root:

```json
{
  "token_optimization": true,
  "parallel_execution": true,
  "logging_level": "INFO",
  "max_retries": 3,
  "timeout": 60
}
```

### Environment Variables

Required environment variables:
- `MONGODB_URI`: MongoDB connection string
- `RAG_API_KEY`: API key for RAG services
- `APM_SECRET`: Secret for APM framework

## Integration with Cursor.ai

1. Open Cursor.ai
2. Import GENXAIS Framework as SDK
3. Configure SDK settings
4. Test integration with sample commands

## Troubleshooting

### Common Issues

1. MongoDB Connection
   ```
   Error: Could not connect to MongoDB
   Solution: Check if MongoDB is running and URI is correct
   ```

2. Missing Dependencies
   ```
   Error: Module not found
   Solution: Run pip install -r requirements.txt
   ```

3. Initialization Fails
   ```
   Error: Could not initialize framework
   Solution: Check permissions and MongoDB connection
   ```

## Next Steps

- Read the [API Reference](api_reference.md)
- Explore [Development Modes](modes.md)
- Check [Integration Guide](integration.md)

## Support

If you encounter any issues:
1. Check the troubleshooting guide
2. Search existing GitHub issues
3. Create a new issue if needed

## Updates

To update GENXAIS Framework:

```bash
git pull origin main
pip install -r requirements.txt
python -m genxais_sdk upgrade
``` 