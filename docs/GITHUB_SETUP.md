# GitHub Repository Setup & Publishing Guide for Qitcoin

This guide walks through creating your GitHub repository, pushing the Qitcoin codebase, and enabling automated CI/CD builds.

---

## Step 1: Create a New GitHub Repository

1. Open your browser and go to: [https://github.com/new](https://github.com/new).
2. Set the repository details:
   - **Repository name**: `qitcoin` (or `qitcoin-core`)
   - **Description**: `Qitcoin Core (QTC) - Standalone Layer-1 PoW Blockchain (1 Trillion Supply)`
   - **Visibility**: Public (or Private while you test)
   - **Initialize with README**: **UNCHECK** (leave unchecked, since our project already has full files!)
3. Click **Create repository**.

---

## Step 2: Initialize Git and Push from Local Laptop

Open PowerShell on your computer and run:

```powershell
cd c:\Users\marti\Downloads\bountyhunter-os-main\qitcoin

# Initialize git repository (if not already initialized)
git init

# Configure your git identity
git config user.name "Your Name"
git config user.email "your-email@example.com"

# Stage all files
git add .

# Create initial commit
git commit -m "feat: initial Qitcoin (QTC) core framework, 1T supply consensus, genesis miner, and localhost explorer"

# Set default branch to main
git branch -M main

# Link to your new GitHub repository (replace with your GitHub username)
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/qitcoin.git

# Push the codebase to GitHub
git push -u origin main
```

---

## Step 3: Automated CI/CD Workflows (`.github/workflows/`)

The repository includes pre-configured GitHub Actions workflows:
- **`blueprint-lint.yml`**: Verifies documentation, code formatting, and supply calculations on every commit.
- **`build-binaries.yml`**: Compiles `qitcoind` and `qitcoin-cli` across Ubuntu Linux and Windows, attaching signed artifacts to your GitHub Releases.

To trigger a release build, create a git tag:
```powershell
git tag -a v0.1.0-testnet -m "Qitcoin Testnet v0.1.0 Release Candidate"
git push origin v0.1.0-testnet
```
GitHub Actions will automatically build and publish release binaries!
