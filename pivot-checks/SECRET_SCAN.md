# Secret scan report (2026-10-16)
Patterns: sk-, sk-or-, ghp_, github_pat_, gho_, hf_[A-Za-z0-9]{20,}, AKIA, "Bearer ", PEM private-key headers, OPENROUTER_API_KEY=value, .env/credential files, email addresses.
Excluded: venv/, ad/ and dyn/ upstream clones (see UPSTREAM_MANIFEST.md), .git, .env*, *.pem/*.key/credentials*/.netrc, __pycache__, release.zip, rankflip/upstream/cmp.json (GitHub contributor metadata with real emails).
Redacted: 3 real author email addresses in papers/*.txt (public arXiv text) replaced with <email-redacted>.
Accepted false positives: "BEGIN OPENSSH PRIVATE KEY" header only (no key material) in AgentDyn injection-task ground truth (drift/, release/results/gt_audit_agentdyn_v1.json, review/ and release/inputs/RECALL_PACKET.md); "task-..." word in papers/2610.00651.txt matching sk-.
Emails remaining are synthetic benchmark fixtures (bluesparrowtech, example/.test/.invalid, AgentDojo persona gmail addresses), github-noreply, and security@facebook.com (fixture).
Result: CLEAN - no tokens, keys, or credentials found.
