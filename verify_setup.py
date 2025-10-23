"""Verify Migrion setup and dependencies."""
import sys
from pathlib import Path

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python version {version.major}.{version.minor} is too old. Need 3.8+")
        return False

def check_dependencies():
    """Check if required packages are installed."""
    required = [
        'streamlit', 'pandas', 'numpy', 'plotly', 'pymongo',
        'google.generativeai', 'dotenv', 'faker', 'networkx',
        'pyvis', 'sklearn', 'seaborn', 'matplotlib'
    ]

    missing = []
    for package in required:
        try:
            if package == 'google.generativeai':
                __import__('google.generativeai')
            elif package == 'dotenv':
                __import__('dotenv')
            elif package == 'sklearn':
                __import__('sklearn')
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing.append(package)

    return len(missing) == 0

def check_env_file():
    """Check if .env file exists."""
    env_path = Path('.env')
    if env_path.exists():
        print("✅ .env file exists")

        # Check if keys are set
        from dotenv import load_dotenv
        import os
        load_dotenv()

        gemini_key = os.getenv('GEMINI_API_KEY', '')
        if gemini_key and gemini_key != 'your_gemini_api_key_here':
            print("✅ GEMINI_API_KEY is set")
        else:
            print("⚠️  GEMINI_API_KEY not set or using placeholder")
            print("   Get your key from https://ai.google.dev/")

        mongodb_uri = os.getenv('MONGODB_URI', '')
        if mongodb_uri and mongodb_uri != 'your_mongodb_connection_string_here':
            print("✅ MONGODB_URI is set")
        else:
            print("ℹ️  MONGODB_URI not set (optional for migration execution)")

        return True
    else:
        print("❌ .env file not found")
        print("   Copy .env.example to .env and add your API keys")
        return False

def check_data_files():
    """Check if example data exists."""
    orange_league_path = Path('data/examples/orange_league')
    olist_path = Path('Olist ecommerce dataset (Brazil)')

    checks = []

    if orange_league_path.exists():
        csv_files = list(orange_league_path.glob('*.csv'))
        print(f"✅ Orange League data: {len(csv_files)} CSV files")
        checks.append(True)
    else:
        print("❌ Orange League data not found")
        print("   Run: python src/modules/data_generator.py")
        checks.append(False)

    if olist_path.exists():
        csv_files = list(olist_path.glob('*.csv'))
        print(f"✅ Olist data: {len(csv_files)} CSV files")
        checks.append(True)
    else:
        print("⚠️  Olist data directory not found (optional)")
        checks.append(True)  # Not critical

    return all(checks)

def check_directory_structure():
    """Check if all required directories exist."""
    required_dirs = [
        'src/agents',
        'src/modules',
        'src/pages',
        'src/utils',
        '.streamlit',
        'data/examples',
        'outputs',
        'logs'
    ]

    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - NOT FOUND")
            all_exist = False

    return all_exist

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Migrion - Setup Verification")
    print("=" * 60)

    print("\n[1/5] Checking Python Version...")
    python_ok = check_python_version()

    print("\n[2/5] Checking Dependencies...")
    deps_ok = check_dependencies()

    print("\n[3/5] Checking Environment Variables...")
    env_ok = check_env_file()

    print("\n[4/5] Checking Directory Structure...")
    dirs_ok = check_directory_structure()

    print("\n[5/5] Checking Data Files...")
    data_ok = check_data_files()

    print("\n" + "=" * 60)
    if all([python_ok, deps_ok, env_ok, dirs_ok, data_ok]):
        print("SUCCESS: All checks passed! You're ready to run Migrion.")
        print("\nNext steps:")
        print("   1. streamlit run app.py")
        print("   2. Open http://localhost:8501 in your browser")
        print("   3. Try the demo or create a new project")
    else:
        print("WARNING: Some checks failed. Please fix the issues above.")
        print("\nSee QUICKSTART.md for detailed setup instructions")
    print("=" * 60)

if __name__ == "__main__":
    main()
