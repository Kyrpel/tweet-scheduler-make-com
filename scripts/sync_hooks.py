import json
import os

def sync_hooks():
    # Read the shared JSON file
    with open('shared/hooks.json', 'r') as f:
        hooks_data = json.load(f)
    
    # Generate Python file
    python_content = '''"""Shared viral hooks configuration used by both frontend and backend."""

VIRAL_HOOKS = ''' + json.dumps(hooks_data, indent=4)
    
    with open('backend/hooks_config.py', 'w') as f:
        f.write(python_content)
    
    # Generate JavaScript file
    js_content = '''// Auto-generated from shared/hooks.json
export const HOOK_CATEGORIES = ''' + json.dumps(hooks_data, indent=2)
    
    with open('src/config/hooks.js', 'w') as f:
        f.write(js_content)

if __name__ == "__main__":
    sync_hooks() 