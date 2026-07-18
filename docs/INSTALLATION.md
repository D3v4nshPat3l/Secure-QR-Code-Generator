# Installation Guide

This guide explains how to install and run **Secure QR Code Generator** on Windows, Linux, Kali Linux, and macOS.

---

## Requirements

You need:

- Python 3.10 or newer;
- an internet connection during dependency installation;
- Git when cloning the repository;
- permission to create files in the installation directory.

The project installs these main Python dependencies:

- `cryptography`;
- `opencv-python-headless`;
- `Pillow`;
- `qrcode`.

---

# Windows installation

## Method 1: Automatic installation with `install.bat`

This is the easiest Windows method.

### Step 1: Install Python

Download Python 3.10 or newer.

During installation, enable:

```text
Add python.exe to PATH
```

Complete the installation and open a new PowerShell or Command Prompt window.

### Step 2: Verify Python

```powershell
python --version
```

Expected:

```text
Python 3.10.x
```

A newer version is also acceptable.

### Step 3: Verify Git

```powershell
git --version
```

When Git is unavailable, install Git for Windows and reopen the terminal.

### Step 4: Clone the repository

```powershell
Set-Location "$HOME\Downloads"
git clone https://github.com/D3v4nshPat3l/Secure-QR-Code-Generator.git
Set-Location ".\Secure-QR-Code-Generator"
```

### Step 5: Run the installer

```powershell
.\install.bat
```

The installer:

1. moves to the project directory;
2. confirms that `python` is available;
3. creates `venv`;
4. activates the environment;
5. upgrades `pip`;
6. installs the package;
7. generates a self-test QR.

### Step 6: Run the application

```powershell
.\run.bat
```

### Step 7: Try a command

```powershell
.\run.bat generate --type url --url example.com --filename example --yes
```

Check:

```text
output\example.png
```

---

## Method 2: Manual Windows installation

### Step 1: Open PowerShell in the repository

```powershell
Set-Location "C:\path\to\Secure-QR-Code-Generator"
```

### Step 2: Create a virtual environment

```powershell
python -m venv venv
```

### Step 3: Activate it

```powershell
.\venv\Scripts\Activate.ps1
```

When PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

The prompt should begin with:

```text
(venv)
```

### Step 4: Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### Step 5: Install the project

```powershell
python -m pip install -e .
```

### Step 6: Verify the command

```powershell
secure-qr --help
secure-qr self-test
```

### Step 7: Start interactive mode

```powershell
secure-qr interactive
```

---

## Method 3: Windows Command Prompt

Create the environment:

```bat
python -m venv venv
```

Activate:

```bat
venv\Scripts\activate.bat
```

Install:

```bat
python -m pip install --upgrade pip
python -m pip install -e .
```

Run:

```bat
secure-qr interactive
```

---

## Windows executable

When a release includes `secure-qr.exe`:

1. open the repository’s **Releases** page;
2. download `secure-qr.exe`;
3. place it in a dedicated folder;
4. open PowerShell in that folder;
5. run:

```powershell
.\secure-qr.exe --help
```

Interactive mode:

```powershell
.\secure-qr.exe interactive
```

Example:

```powershell
.\secure-qr.exe generate --type url --url example.com --yes
```

Windows SmartScreen may warn about an unsigned community executable. Verify that it came from the official repository release before allowing it.

---

# Linux and Kali Linux installation

## Method 1: Automatic installation

### Step 1: Install required packages

Debian, Ubuntu, and Kali:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip
```

### Step 2: Verify versions

```bash
python3 --version
git --version
```

### Step 3: Clone the repository

```bash
git clone https://github.com/D3v4nshPat3l/Secure-QR-Code-Generator.git
cd Secure-QR-Code-Generator
```

### Step 4: Make scripts executable

```bash
chmod +x install.sh run.sh
```

### Step 5: Install

```bash
./install.sh
```

The script creates `venv`, installs the project, and generates a test QR.

### Step 6: Run

```bash
./run.sh
```

### Step 7: Generate a QR

```bash
./run.sh generate --type url --url example.com --yes
```

---

## Method 2: Manual Linux/Kali installation

```bash
git clone https://github.com/D3v4nshPat3l/Secure-QR-Code-Generator.git
cd Secure-QR-Code-Generator

python3 -m venv venv
source venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e .

secure-qr self-test
secure-qr interactive
```

---

# macOS installation

## Step 1: Install Python and Git

Using Homebrew:

```bash
brew install python git
```

## Step 2: Clone

```bash
git clone https://github.com/D3v4nshPat3l/Secure-QR-Code-Generator.git
cd Secure-QR-Code-Generator
```

## Step 3: Create and activate the environment

```bash
python3 -m venv venv
source venv/bin/activate
```

## Step 4: Install

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

## Step 5: Verify

```bash
secure-qr self-test
secure-qr --help
```

---

# Installing a release wheel

When a release provides a `.whl` file:

```bash
python -m venv venv
```

Activate the environment, then install the wheel:

```bash
python -m pip install secure_qr_code_generator-0.2.0-py3-none-any.whl
```

Verify:

```bash
secure-qr --help
```

---

# Reproducible dependency installation

The repository contains `requirements.lock` with pinned direct runtime dependencies.

Create and activate a virtual environment, then run:

```bash
python -m pip install -r requirements.lock
python -m pip install --no-deps -e .
```

The file pins direct dependencies. It is not a full hash-locked record of every transitive package.

---

# Development installation

```bash
python -m venv venv
```

Activate it, then:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run:

```bash
python -m pytest -q
ruff check .
```

---

# Confirming a successful installation

All of these should work:

```bash
secure-qr --help
secure-qr self-test
secure-qr generate --type text --text "Installation successful" --yes
```

The self-test performs:

1. payload validation;
2. QR generation;
3. atomic write;
4. PNG decode;
5. exact payload comparison;
6. temporary-file cleanup.

---

# Updating the project

Inside the repository:

```bash
git pull --ff-only
```

Activate the environment and reinstall:

```bash
python -m pip install --upgrade -e .
```

For development dependencies:

```bash
python -m pip install --upgrade -e ".[dev]"
```

---

# Removing the project

When installed only inside the project virtual environment:

1. deactivate the environment:

```bash
deactivate
```

2. delete the `venv` directory;
3. delete the cloned repository when it is no longer needed.

If installed into another active environment:

```bash
python -m pip uninstall secure-qr-code-generator
```

---

# Troubleshooting

## `python` is not recognized on Windows

Check:

```powershell
where.exe python
```

Install Python and enable `Add python.exe to PATH`. Close and reopen PowerShell.

## `py` is not recognized

The Windows `py` launcher is optional. Use:

```powershell
python
```

instead.

## Python is too old

Check:

```bash
python --version
```

Install Python 3.10 or newer and recreate the virtual environment.

## `No module named venv`

Debian, Ubuntu, or Kali:

```bash
sudo apt install python3-venv
```

## PowerShell activation is blocked

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

This changes policy only for the current PowerShell process.

## `secure-qr` is not recognized

Confirm the environment is active and reinstall:

```bash
python -m pip install -e .
```

Alternative execution:

```bash
python -m secure_qr.cli --help
```

## OpenCV installation fails

Upgrade packaging tools:

```bash
python -m pip install --upgrade pip setuptools wheel
```

Then:

```bash
python -m pip install opencv-python-headless
```

## QR verification fails

Try a simple black-on-white QR:

```bash
secure-qr generate \
  --type text \
  --text "verification test" \
  --fill-color black \
  --back-color white \
  --error-correction H \
  --yes
```

Use `--no-verify` only for diagnostics.

## Output already exists

Use a new filename or explicitly replace it:

```bash
secure-qr generate \
  --type text \
  --text "replacement" \
  --filename existing_name \
  --overwrite \
  --yes
```

## URL DNS warning

When offline:

```bash
secure-qr generate \
  --type url \
  --url example.com \
  --no-dns-check \
  --yes
```

## Linux permission denied for scripts

```bash
chmod +x install.sh run.sh
```

## Windows batch file opens and closes immediately

Open PowerShell manually, enter the project directory, and run:

```powershell
.\install.bat
```

This keeps the error visible.

---

# Next steps

After installation:

1. read the root [README](../README.md);
2. review [FEATURES.md](FEATURES.md);
3. use [COMMANDS.md](COMMANDS.md);
4. read the [threat model](threat-model.md);
5. never commit passwords, Wi-Fi secrets, or private keys.
