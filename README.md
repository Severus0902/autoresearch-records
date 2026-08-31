# AutoResearch

AutoResearch is a small local research automation system that connects four things:

- Zotero Local API for literature records.
- Markdown files for ideas, experiments, and results.
- Git/GitHub for a complete change log.
- SSH for running commands on a research server.

The project is intentionally dependency-free and works with Python 3.8+.

## Quick Start

Keep Zotero Desktop open and make sure local API access is enabled:

`http://127.0.0.1:23119/api/`

Create your local config:

```powershell
Copy-Item config.example.json config.local.json
```

Edit `config.local.json` and fill in:

- `server.ssh_target`, for example `user@server.example.com`
- `server.remote_workdir`, for example `/home/user/research/project`
- `git.remote`, usually `origin`
- `git.branch`, usually `main`

Initialize Git and connect GitHub:

```powershell
python -m autoresearch git setup-remote --url git@github.com:USER/REPO.git
python -m autoresearch git checkpoint -m "Initialize AutoResearch"
```

## Common Commands

Check local system status:

```powershell
python -m autoresearch status
```

Sync Zotero top-level items into `data/zotero/items.json` and `data/zotero/library.md`:

```powershell
python -m autoresearch zotero sync
```

Create an idea note:

```powershell
python -m autoresearch idea new --title "Fault attack experiment plan"
```

Index Markdown notes:

```powershell
python -m autoresearch notes index
```

Run a quick command on the server:

```powershell
python -m autoresearch remote run --cmd "hostname && pwd"
```

Run and record an experiment:

```powershell
python -m autoresearch experiment run --name bus-fault-baseline --cmd "python train.py --config configs/baseline.yaml"
```

Create a Git checkpoint and push it:

```powershell
python -m autoresearch git checkpoint -m "Record baseline experiment"
```

## Research Loop

1. Add or update references in Zotero.
2. Run `python -m autoresearch zotero sync`.
3. Write ideas in `docs/ideas`.
4. Run experiments through `python -m autoresearch experiment run`.
5. Record interpretations in `docs/results`.
6. Use `python -m autoresearch git checkpoint -m "..."`

This keeps literature, ideas, experiment logs, results, and code changes in one versioned project.

## Literature Review Notes

Every research report should include a paper table with:

- Zotero citation key.
- Method or paper name.
- Accepted or published venue.
- Source link used to verify the venue.
- Status, such as formal conference paper, journal paper, arXiv/CoRR preprint, or needs recheck.

If a cited paper is added from outside the current Zotero library, add it to Zotero first and then rerun `python -m autoresearch zotero sync`.
