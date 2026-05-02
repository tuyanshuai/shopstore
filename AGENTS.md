# AGENTS.md

## Cursor Cloud specific instructions

### Architecture

Single-process Python 3 application with zero external dependencies. `backend/server.py` serves both the REST API and static frontend files on port 8000. No database, no build step, no package manager — Python standard library only.

### Running the dev server

```bash
python3 backend/server.py
```

Server starts at `http://localhost:8000`. See `README.md` for API endpoints.

### Key caveats

- All data (products, orders, newsletter subscribers) is stored in-memory; restarting the server resets state.
- No automated test suite exists in the repository. Verify changes via API calls (`curl`) and/or browser testing.
- No linter or formatter is configured. Use standard Python and web best practices.
- The frontend is vanilla HTML/CSS/JS served as static files from `frontend/`; no transpilation or bundling is needed.
