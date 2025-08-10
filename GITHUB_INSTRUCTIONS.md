# Instructions for Pushing to GitHub

Follow these steps to push your Coin Price Monitor project to GitHub:

## 1. Create a New GitHub Repository

1. Go to [GitHub](https://github.com/) and sign in to your account.
2. Click on the "+" icon in the top-right corner and select "New repository".
3. Enter "coin_price_monitor_project" as the repository name.
4. (Optional) Add a description for your repository.
5. Choose whether the repository should be public or private.
6. Do NOT initialize the repository with a README, .gitignore, or license as we already have these files locally.
7. Click "Create repository".

## 2. Connect Your Local Repository to GitHub

After creating the repository, GitHub will show you commands to push an existing repository. Use the following commands:

```bash
# Add the GitHub repository as a remote (replace 'yourusername' with your GitHub username)
git remote add origin https://github.com/yourusername/coin_price_monitor_project.git

# Push your local repository to GitHub
git push -u origin main
```

## 3. Update README.md

After pushing to GitHub, update the README.md file to reflect the correct GitHub repository URL:

```bash
# Open README.md in your favorite editor and update the clone URL
# Replace 'yourusername' with your actual GitHub username in these lines:
# git clone https://github.com/yourusername/coin_price_monitor_project.git
```

## 4. Commit and Push the Updated README

```bash
git add README.md
git commit -m "Update README with correct GitHub repository URL"
git push
```

## 5. Verify

Visit your GitHub repository at `https://github.com/yourusername/coin_price_monitor_project` to verify that all files have been pushed correctly.