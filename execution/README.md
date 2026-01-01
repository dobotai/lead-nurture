# Execution Directory

This directory contains deterministic Python scripts that handle the actual work.

## Principles

1. **Deterministic**: Same inputs = same outputs
2. **Testable**: Can be run and verified independently
3. **Reliable**: Handle errors gracefully
4. **Fast**: Optimized for performance

## Script Template

```python
#!/usr/bin/env python3
"""
Brief description of what this script does.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main(param1, param2):
    """
    Main function description.

    Args:
        param1: Description
        param2: Description

    Returns:
        Description of return value

    Raises:
        Exception: When something goes wrong
    """
    # Implementation here
    pass

if __name__ == "__main__":
    # Example usage
    result = main("example1", "example2")
    print(result)
```

## Best Practices

1. Use environment variables for credentials (from .env)
2. Include docstrings for all functions
3. Handle errors with clear messages
4. Return structured data (dict/list)
5. Keep functions focused and single-purpose
6. Add logging for debugging
7. Test with sample data first

## Common Patterns

### Loading Environment Variables
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('API_KEY_NAME')
```

### Error Handling
```python
try:
    result = api_call()
except Exception as e:
    print(f"Error: {str(e)}")
    # Handle gracefully
    return None
```

### File Operations
```python
# Always use .tmp/ for intermediate files
output_path = os.path.join('.tmp', 'output.json')
with open(output_path, 'w') as f:
    json.dump(data, f)
```

## Testing Scripts

Run scripts directly to test:
```bash
python execution/script_name.py
```

## Dependencies

Install all dependencies:
```bash
pip install -r execution/requirements.txt
```
