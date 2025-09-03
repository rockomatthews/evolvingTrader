# Quick Start Guide - Fix Virtual Environment Issues

## 🚨 **Problem: ModuleNotFoundError**

You're getting `ModuleNotFoundError: No module named 'numpy'` because you're not in the virtual environment.

## 🔧 **Quick Fix**

### **Option 1: Use the Run Scripts (Easiest)**

```bash
# Make scripts executable
chmod +x run_backtest.sh run_live.sh run_dashboard.sh

# Run backtest
./run_backtest.sh

# Run live trading
./run_live.sh

# Run dashboard
./run_dashboard.sh
```

### **Option 2: Manual Activation**

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. You should see (venv) in your prompt
(venv) MacBook-Pro:evolvingTrader home$

# 3. Now run any command
python main.py backtest
python main.py live
python main.py dashboard
```

### **Option 3: Check Virtual Environment**

```bash
# Check if virtual environment exists
ls -la venv/

# If it doesn't exist, create it
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

## 🎯 **Step-by-Step Solution**

### **Step 1: Verify Virtual Environment**
```bash
# Check if venv directory exists
ls -la | grep venv
```

### **Step 2: Activate Virtual Environment**
```bash
# Activate (you should see (venv) in prompt)
source venv/bin/activate
```

### **Step 3: Verify Packages**
```bash
# Check if numpy is installed
python -c "import numpy; print('numpy version:', numpy.__version__)"
```

### **Step 4: Install Missing Packages**
```bash
# If packages are missing, install them
pip install -r requirements.txt
```

### **Step 5: Run System**
```bash
# Now you can run the system
python main.py backtest
```

## 🔍 **Troubleshooting**

### **"venv directory not found"**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **"Permission denied" on scripts**
```bash
# Make scripts executable
chmod +x run_backtest.sh run_live.sh run_dashboard.sh
```

### **"Packages not installing"**
```bash
# Try upgrading pip first
pip install --upgrade pip
pip install -r requirements.txt
```

### **"Still getting import errors"**
```bash
# Check which Python you're using
which python
python --version

# Make sure you're in the virtual environment
echo $VIRTUAL_ENV
```

## 🚀 **Quick Commands**

### **Run Backtest:**
```bash
./run_backtest.sh
```

### **Run Live Trading:**
```bash
./run_live.sh
```

### **Run Dashboard:**
```bash
./run_dashboard.sh
```

### **Manual Activation:**
```bash
source venv/bin/activate
python main.py backtest
```

## 💡 **Pro Tips**

### **Always activate virtual environment first:**
```bash
# Before running any Python commands
source venv/bin/activate
```

### **Check if you're in virtual environment:**
```bash
# You should see (venv) in your prompt
(venv) MacBook-Pro:evolvingTrader home$
```

### **Deactivate when done:**
```bash
deactivate
```

## 🆘 **Still Having Issues?**

### **Try this complete reset:**
```bash
# Remove old virtual environment
rm -rf venv

# Create new one
python3 -m venv venv

# Activate
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Test
python -c "import numpy; print('Success!')"
```

The key is **always activate the virtual environment first** before running any Python commands!