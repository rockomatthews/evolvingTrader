# Complete Installation Guide

## 🚨 **Problem: Virtual Environment Not Found**

You're getting `bash: venv/bin/activate: No such file or directory` because the virtual environment hasn't been created yet.

## 🔧 **Complete Setup Solution**

### **Option 1: Use the Complete Setup Script (Recommended)**

```bash
# Make the script executable
chmod +x setup_complete.sh

# Run the complete setup
./setup_complete.sh
```

### **Option 2: Manual Setup**

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install requirements
pip install -r requirements.txt

# 5. Create directories
mkdir -p logs data results backtests

# 6. Create .env file
cp .env.example .env
```

## 🎯 **Step-by-Step Instructions**

### **Step 1: Create Virtual Environment**
```bash
python3 -m venv venv
```

### **Step 2: Activate Virtual Environment**
```bash
source venv/bin/activate
```

### **Step 3: Verify Activation**
```bash
# You should see (venv) in your prompt
(venv) MacBook-Pro:evolvingTrader home$
```

### **Step 4: Install Packages**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### **Step 5: Test Installation**
```bash
python -c "import numpy; print('numpy version:', numpy.__version__)"
```

### **Step 6: Create .env File**
```bash
cp .env.example .env
nano .env  # Edit with your API keys
```

### **Step 7: Run System**
```bash
python main.py backtest
```

## 🚀 **Quick Commands**

### **Complete Setup (One Command):**
```bash
chmod +x setup_complete.sh && ./setup_complete.sh
```

### **After Setup:**
```bash
# Activate virtual environment
source venv/bin/activate

# Run backtest
python main.py backtest
```

## 🔍 **Troubleshooting**

### **"python3: command not found"**
```bash
# Install Python 3
brew install python3
```

### **"Permission denied"**
```bash
# Make scripts executable
chmod +x setup_complete.sh
chmod +x run_backtest.sh
chmod +x run_live.sh
chmod +x run_dashboard.sh
```

### **"pip: command not found"**
```bash
# Install pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
```

### **"Package installation fails"**
```bash
# Try with --user flag
pip install --user -r requirements.txt
```

## 📋 **What the Setup Script Does**

1. ✅ **Checks Python version**
2. ✅ **Creates virtual environment**
3. ✅ **Activates virtual environment**
4. ✅ **Upgrades pip**
5. ✅ **Installs all requirements**
6. ✅ **Creates necessary directories**
7. ✅ **Creates .env file from template**
8. ✅ **Provides next steps**

## 🎯 **After Setup**

### **Always activate virtual environment first:**
```bash
source venv/bin/activate
```

### **Then run any command:**
```bash
python main.py backtest
python main.py live
python main.py dashboard
```

### **Or use the run scripts:**
```bash
./run_backtest.sh
./run_live.sh
./run_dashboard.sh
```

## 💡 **Pro Tips**

### **Check if virtual environment exists:**
```bash
ls -la venv/
```

### **Check if you're in virtual environment:**
```bash
echo $VIRTUAL_ENV
# Should show: /Users/home/evolved/evolvingTrader/venv
```

### **Deactivate when done:**
```bash
deactivate
```

## 🆘 **Still Having Issues?**

### **Try this complete reset:**
```bash
# Remove everything
rm -rf venv
rm -rf __pycache__
rm -rf src/__pycache__

# Start fresh
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

The key is to **create the virtual environment first** before trying to activate it!