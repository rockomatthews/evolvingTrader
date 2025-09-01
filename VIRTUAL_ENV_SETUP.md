# Virtual Environment Setup Guide

## 🐍 Python 3.13 Externally Managed Environment Fix

If you're getting the "externally-managed-environment" error, this is because Python 3.13 (installed via Homebrew) prevents installing packages system-wide to protect your system.

## 🚀 Quick Fix

### **Option 1: Use the Updated Setup Script (Recommended)**
```bash
# Run the updated setup script
python setup.py

# The script will automatically create a virtual environment
```

### **Option 2: Manual Setup**
```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# 3. Install requirements
pip install -r requirements.txt

# 4. Run setup
python setup.py
```

### **Option 3: Use Activation Scripts**
```bash
# Linux/Mac
chmod +x activate.sh
./activate.sh

# Windows
activate.bat
```

## 🔧 What the Updated Setup Does

The updated `setup.py` script now:

1. **Automatically creates** a virtual environment in the `venv/` directory
2. **Installs packages** in the virtual environment (not system-wide)
3. **Provides clear instructions** for activation
4. **Falls back** to user installation if virtual environment fails

## 📁 Project Structure After Setup

```
evolvingTrader/
├── venv/                    # Virtual environment (created automatically)
│   ├── bin/                 # Python executables
│   ├── lib/                 # Installed packages
│   └── ...
├── src/                     # Source code
├── .env                     # Environment variables
├── requirements.txt         # Dependencies
├── activate.sh              # Linux/Mac activation script
├── activate.bat             # Windows activation script
└── ...
```

## 🎯 Running the System

### **Always activate the virtual environment first:**

```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### **Then run any command:**
```bash
python main.py backtest
python main.py live
python main.py dashboard
```

### **To deactivate:**
```bash
deactivate
```

## 🔍 Troubleshooting

### **"Command not found" errors:**
- Make sure you've activated the virtual environment
- Check that the virtual environment was created successfully

### **"Module not found" errors:**
- Ensure you're in the activated virtual environment
- Reinstall requirements: `pip install -r requirements.txt`

### **Permission errors:**
- On Linux/Mac, you might need: `chmod +x activate.sh`
- On Windows, run Command Prompt as Administrator

## 💡 Pro Tips

### **Create an alias for easy activation:**
```bash
# Add to your ~/.bashrc or ~/.zshrc
alias evolve="cd /path/to/evolvingTrader && source venv/bin/activate"
```

### **Use the activation scripts:**
- **Linux/Mac**: `./activate.sh`
- **Windows**: `activate.bat`

### **Check if virtual environment is active:**
```bash
# You should see (venv) in your prompt
(venv) user@computer:~/evolvingTrader$
```

## 🆘 Still Having Issues?

### **Alternative: Use pipx (if available)**
```bash
# Install pipx
brew install pipx

# Install packages with pipx
pipx install --include-deps -r requirements.txt
```

### **Alternative: Use conda**
```bash
# Create conda environment
conda create -n evolvingtrader python=3.11
conda activate evolvingtrader
pip install -r requirements.txt
```

### **Alternative: Use Docker**
```bash
# Create Dockerfile
cat > Dockerfile << EOF
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
EOF

# Build and run
docker build -t evolvingtrader .
docker run -it evolvingtrader
```

The virtual environment approach is the most reliable and recommended method for Python development!