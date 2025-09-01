"""
Setup script for EvolvingTrader
"""
import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        sys.exit(1)

def create_env_file():
    """Create .env file from template"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("Creating .env file from template...")
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✓ .env file created")
        print("⚠️  Please edit .env file with your API keys and configuration")
    elif env_file.exists():
        print("✓ .env file already exists")
    else:
        print("⚠️  No .env.example file found")

def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'data', 'results', 'backtests']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def check_api_keys():
    """Check if API keys are configured"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found. Please create it with your API keys")
        return
    
    with open(env_file, 'r') as f:
        content = f.read()
    
    required_keys = [
        'BINANCE_API_KEY',
        'BINANCE_SECRET_KEY',
        'OPENAI_API_KEY',
        'PINECONE_API_KEY',
        'DATABASE_URL',
        'REDIS_URL',
        'UPSTASH_REDIS_REST_URL',
        'UPSTASH_REDIS_REST_TOKEN'
    ]
    
    missing_keys = []
    for key in required_keys:
        if f"{key}=your_" in content or f"{key}=" not in content:
            missing_keys.append(key)
    
    if missing_keys:
        print("⚠️  Missing or placeholder API keys:")
        for key in missing_keys:
            print(f"   - {key}")
        print("Please update your .env file with actual API keys")
        print("\nFor Neon.tech database setup:")
        print("1. Go to https://neon.tech")
        print("2. Create a new project")
        print("3. Copy the connection string to DATABASE_URL in .env")
        print("\nFor Upstash Redis setup:")
        print("1. Go to https://upstash.com")
        print("2. Create a new Redis database")
        print("3. Copy the connection details to REDIS_URL, UPSTASH_REDIS_REST_URL, and UPSTASH_REDIS_REST_TOKEN in .env")
    else:
        print("✓ API keys appear to be configured")

def setup_database():
    """Setup database tables"""
    try:
        print("Setting up database...")
        
        # Import here to avoid issues if dependencies aren't installed yet
        import asyncio
        from src.database.connection import db_manager
        
        async def init_db():
            try:
                await db_manager.initialize()
                print("✓ Database tables created successfully")
            except Exception as e:
                print(f"⚠️  Database setup failed: {e}")
                print("Make sure your DATABASE_URL is correct in .env file")
        
        asyncio.run(init_db())
        
    except ImportError:
        print("⚠️  Database setup skipped - dependencies not installed yet")
    except Exception as e:
        print(f"⚠️  Database setup failed: {e}")

def main():
    """Main setup function"""
    print("EvolvingTrader Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Create directories
    create_directories()
    
    # Install requirements
    install_requirements()
    
    # Create .env file
    create_env_file()
    
    # Check API keys
    check_api_keys()
    
    # Setup database
    setup_database()
    
    print("\n" + "=" * 50)
    print("Setup completed!")
    print("\nNext steps:")
    print("1. Edit .env file with your API keys and Neon.tech database URL")
    print("2. Run backtest: python main.py backtest")
    print("3. Run live trading: python main.py live")
    print("4. Run dashboard: python main.py dashboard")
    print("\nFor help: python main.py --help")

if __name__ == "__main__":
    main()