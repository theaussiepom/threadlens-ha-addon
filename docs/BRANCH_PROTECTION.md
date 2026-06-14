# Branch protection for `main`

Apply these settings in **GitHub → Settings → Branches → Branch protection rules** for `main` if they cannot be applied automatically.

## Required settings

- [ ] **Require a pull request before merging**
- [ ] **Require status checks to pass before merging**
  - Required check: `test`
- [ ] **Require branches to be up to date before merging** (if practical)
- [ ] **Do not allow bypassing the above settings** (enforce for administrators)
- [ ] **Restrict direct pushes** — no direct commits to `main`
- [ ] **Allow force pushes** — disabled
- [ ] **Allow deletions** — disabled
- [ ] **Merge methods** — prefer **Squash merge** only

## CLI attempt

Maintainers with admin access can try:

```bash
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  repos/theaussiepom/threadlens-ha-addon/branches/main/protection \
  -f required_status_checks[strict]=true \
  -f required_status_checks[contexts][]=test \
  -f enforce_admins=true \
  -f required_pull_request_reviews[required_approving_review_count]=0 \
  -f restrictions=null
```

GitHub's branch protection API evolves; adjust fields if the command fails and configure via the UI instead.
