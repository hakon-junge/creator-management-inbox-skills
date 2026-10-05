#!/usr/bin/env bash
# Scan the repo for anything that must never be published.
#
# Built-in checks: credential-shaped strings, OAuth client/token files, private
# keys, real-looking email addresses, and personal data files.
#
# Private checks: names of companies, people or products that must not appear
# (e.g. a former employer). They are NOT listed in this public file - put one
# regex per line in `.leak-patterns.local` (git-ignored), and/or set the
# LEAK_PATTERNS environment variable (CI reads it from a repository secret).
#
# Exit 1 on any finding. Run before every push: ./scripts/leak-scan.sh
set -uo pipefail
cd "$(dirname "$0")/.."
fail=0

scan() {  # label, extended regex, [extra grep flags]
  local label="$1" pattern="$2"; shift 2
  local hits
  hits=$(git ls-files -co --exclude-standard -z | xargs -0 grep -nIE "$@" -- "$pattern" 2>/dev/null \
         | grep -v '^scripts/leak-scan.sh:' \
         | grep -viE '@(example\.(com|org|net)|yourcompany\.com|yourbrand\.com|anthropic\.com)\b|noreply@' || true)
  if [ -n "$hits" ]; then
    echo "FAIL: $label"; echo "$hits" | head -20; echo; fail=1
  else
    echo "ok:   $label"
  fi
}

scan "credential-shaped strings" '(AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|ya29\.[0-9A-Za-z_-]{20,}|1//0[0-9A-Za-z_-]{20,}|GOCSPX-[0-9A-Za-z_-]{10,}|sk-ant-[0-9A-Za-z_-]{10,}|sk-[0-9A-Za-z]{32,}|xox[baprs]-[0-9A-Za-z-]{10,}|ghp_[0-9A-Za-z]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)'
scan "OAuth client ids" '[0-9]{8,}-[0-9a-z]{20,}\.apps\.googleusercontent\.com'
scan "refresh tokens in JSON" '"refresh_token"\s*:\s*"[^"]{10,}"'
scan "email addresses outside .example / placeholders" '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(com|io|co|net|org|de|uk|app|ai)\b' -i

files=$(git ls-files -co --exclude-standard | grep -E '(^|/)(token\.json|client_secret[^/]*\.json|creators_snapshot\.json|runs\.jsonl|\.env)$' || true)
if [ -n "$files" ]; then echo "FAIL: secret or personal-data files present"; echo "$files"; fail=1; else echo "ok:   no secret or personal-data files"; fi

patterns=""
[ -f .leak-patterns.local ] && patterns=$(grep -vE '^\s*(#|$)' .leak-patterns.local | paste -sd'|' -)
if [ -n "${LEAK_PATTERNS:-}" ]; then patterns="${patterns:+$patterns|}$LEAK_PATTERNS"; fi
if [ -n "$patterns" ]; then
  scan "private patterns (names that must not appear)" "$patterns" -i
  hist=$(git log --all -p 2>/dev/null | grep -icE "$patterns" || true)
  if [ "${hist:-0}" != "0" ]; then echo "FAIL: private patterns found in git history ($hist lines) - history must be rewritten before publishing"; fail=1; else echo "ok:   git history clean of private patterns"; fi
else
  echo "warn: no private patterns configured (.leak-patterns.local or LEAK_PATTERNS)"
fi

echo
if [ $fail -ne 0 ]; then echo "LEAK SCAN FAILED - do not push."; exit 1; fi
echo "PASS - nothing found."
