# Agent Recovery commercial app MVP

This directory is the first commercial product surface. It is separate from the old competition judge demo.

The app is intentionally read-only. It renders accepted backend evidence and does not reimplement recovery, approval, containment or restoration decisions in JavaScript.

Generate the owned deterministic sample payload:

```bash
python scripts/build_app_fixture.py
```

Preview locally from the repository root:

```bash
python -m http.server 8080 -d app
```

Then open `http://localhost:8080`.

The next application slices should replace the static owned fixture with an operator API transport, add an incident list backed by persisted evidence, and add assessment export. Write actions remain out of scope until separately designed deterministic action endpoints exist.
