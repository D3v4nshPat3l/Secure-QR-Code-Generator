# Publishing the v0.2 Refactor

The change set is intentionally large. Publish it on a branch and review the generated pull request before merging.

## Linux or macOS

From an existing clone of the repository:

```bash
git switch main
git pull --ff-only
git switch -c security-toolkit-v0.2

# Copy the contents of the prepared Secure-QR-Code-Generator directory over this clone.
# Keep the clone's .git directory.

git add -A
git status --short
git commit -m "Build secure QR security toolkit v0.2"
git push -u origin security-toolkit-v0.2
gh pr create --draft --base main --head security-toolkit-v0.2 \
  --title "Build secure QR security toolkit v0.2" \
  --body-file PR_BODY.md
```

## Windows PowerShell

```powershell
git switch main
git pull --ff-only
git switch -c security-toolkit-v0.2
# Copy all prepared files over the clone, preserving .git.
git add -A
git status --short
git commit -m "Build secure QR security toolkit v0.2"
git push -u origin security-toolkit-v0.2
gh pr create --draft --base main --head security-toolkit-v0.2 --title "Build secure QR security toolkit v0.2" --body-file PR_BODY.md
```

Run these checks before marking the pull request ready:

```bash
python -m pip install -e ".[dev]"
pytest --cov=secure_qr
ruff check .
python -m secure_qr.cli self-test
```
