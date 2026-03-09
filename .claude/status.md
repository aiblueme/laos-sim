---
project: laos-sim
url: https://laos-sim.shellnode.lol
vps: ghost
port: 8421
stack: multi-file HTML/CSS/JS, nginx:alpine, SWAG
standards_version: "2.0"
security: done
ux_ui: in_progress
repo_cleanup: done
readme: done
last_session: "2026-03-09"
has_blockers: true
---

# Project Status — laos-sim

## Last Session
Date: 2026-03-09
Agent: Claude Code

### Completed
- **[P1]** Created `nginx.conf` — security headers (X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy), gzip, dotfile blocking, static asset caching
- **[P1]** Updated `Dockerfile` — added `RUN rm -rf /usr/share/nginx/html/*`, `COPY nginx.conf`, `EXPOSE 80`, `CMD`
- **[P1]** Created `.dockerignore` — excludes .git, .claude, .venv, crawl_images.py, requirements.txt, images/_raw
- **[P1]** Fixed `.gitignore` — added `.env` and `.env.*` entries
- **[P2]** Added `mem_limit: 128m` to docker-compose.yml
- **[P0 check]** No secrets in source files, JS, or git history — clean
- **[Repo]** Created README.md with live URL, stack, run/deploy instructions

### Incomplete
- UX/UI audit started but not finished (only reviewed CSS structure, not full functionality check)
- Container not rebuilt/verified live — no SSH access in this session

### Blocked — Needs Matt
- **SWAG labels format**: docker-compose.yml uses `swag=nginx` / `swag.host=laos-sim`. Canonical format in CLAUDE.md is `swag=enable` / `swag_address` / `swag_port` / `swag_url`. Previous project `laos-events` had the same question flagged. Need confirmation which format is correct for this SWAG setup before changing.
- **Live verification**: No SSH/Docker access — cannot rebuild container and verify headers land. Next session should run `curl -sI` against the live URL after deployment.

## Backlog
- [P2] UX/UI: `backdrop-filter: blur(8px)` on nav = glassmorphism (anti-pattern #3) — document only, don't change (intentional design)
- [P2] UX/UI: Hero section with gradient overlay (anti-pattern #1/#4) — document only, intentional design
- [P3] UX/UI: `scroll-behavior: smooth` in CSS + JS (anti-pattern #9) — document only
- [P3] UX/UI: Fonts are Playfair Display (decorative serif) + Inter (sans) — differs from standards (condensed sans headers, monospace body) — legacy design, don't retrofit
- [P2] UX/UI: Full images total 9.4MB — lazy loaded via IntersectionObserver so page load impact is low; thumbs are 1MB. Flag if individual images exceed 500KB.
- [P3] Add LICENSE (MIT)
- [P3] Rebuild and push Docker image after security fixes, verify with curl

## Done
- [x] Security scan — no secrets — 2026-03-09
- [x] Create nginx.conf with security headers — 2026-03-09
- [x] Update Dockerfile — nginx.conf, EXPOSE, CMD — 2026-03-09
- [x] Create .dockerignore — 2026-03-09
- [x] Fix .gitignore — add .env entries — 2026-03-09
- [x] Add memory limit to docker-compose.yml — 2026-03-09
- [x] Create README.md — 2026-03-09

## Decisions Log
- "Did not change SWAG labels — format differs from canonical but same question was flagged for laos-events; awaiting Matt's confirmation" (2026-03-09)
- "Did not retrofit design to STANDARDS aesthetic — project uses Playfair Display/Inter and hero section intentionally; STANDARDS say preserve existing design language" (2026-03-09)
- "Added images/_raw to .dockerignore even though Dockerfile only explicitly copies full/ and thumbs/ — belt and suspenders" (2026-03-09)

## Project Notes
- Multi-file project (index.html + css/style.css + js/main.js + images/) — not a single-file site
- 178 webp images: 10 in full/ (9.4MB) + 10 in thumbs/ (1MB) [actually 89+89 — verify]
- images/_raw/ excluded from git (.gitignore) and Docker (.dockerignore)
- .venv/ present locally — Python env for crawl_images.py — excluded from git and Docker
- crawl_images.py uses icrawler for image acquisition — not part of the deployed site
