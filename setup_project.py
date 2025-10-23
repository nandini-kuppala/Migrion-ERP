"""Script to set up all remaining project files."""
import os
from pathlib import Path

def create_file(filepath, content):
    """Create a file with content."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created: {filepath}")

# Create __init__.py files
init_files = [
    'src/__init__.py',
    'src/agents/__init__.py',
    'src/modules/__init__.py',
    'src/pages/__init__.py',
]

for file in init_files:
    create_file(file, '"""Package init file."""\n')

print("All __init__.py files created!")
print("\nProject structure is ready!")
print("\nNext steps:")
print("1. Add your GEMINI_API_KEY and MONGODB_URI to .env file")
print("2. Install dependencies: pip install -r requirements.txt")
print("3. Generate synthetic data: python src/modules/data_generator.py")
print("4. Run the app: streamlit run app.py")
