# GitHub Personal Access Token (PAT) Instructions

To push your code to GitHub, you need to generate a Personal Access Token (PAT) and use it for authentication. Follow these steps:

## 1. Generate a Personal Access Token (PAT)

1. Go to [GitHub Settings](https://github.com/settings/profile)
2. Click on "Developer settings" in the left sidebar
3. Click on "Personal access tokens" and then "Tokens (classic)"
4. Click "Generate new token" and then "Generate new token (classic)"
5. Give your token a descriptive name (e.g., "Coin Monitor Project")
6. Select the scopes or permissions you need:
   - At minimum, select "repo" for full control of private repositories
7. Click "Generate token"
8. **IMPORTANT**: Copy your token immediately! You won't be able to see it again.

## 2. Update the Remote URL with Your Token

Replace "TOKEN" in the remote URL with your actual token:

```bash
git remote set-url origin https://YOUR_ACTUAL_TOKEN@github.com/Sharex508/coin-monitor.git
```

For example, if your token is "ghp_abc123def456", the command would be:

```bash
git remote set-url origin https://ghp_abc123def456@github.com/Sharex508/coin-monitor.git
```

## 3. Push Your Code to GitHub

After updating the remote URL with your token, you can push your code:

```bash
git push -u origin main
```

## Alternative: Use SSH Authentication

If you prefer using SSH instead of HTTPS with a token:

1. Generate an SSH key if you don't have one:
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. Add the SSH key to your GitHub account:
   - Copy the public key: `cat ~/.ssh/id_ed25519.pub`
   - Go to GitHub Settings > SSH and GPG keys > New SSH key
   - Paste your key and save

3. Change the remote URL to use SSH:
   ```bash
   git remote set-url origin git@github.com:Sharex508/coin-monitor.git
   ```

4. Push your code:
   ```bash
   git push -u origin main
   ```

## Security Note

Never share your personal access token with anyone or commit it to your repository. Treat it like a password.