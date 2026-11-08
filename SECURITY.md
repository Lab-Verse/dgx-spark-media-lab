# Security and private data

This is an experimental local-workstation guide. It is not a hardened multi-tenant media service. Bind model/ComfyUI APIs to loopback and use your normal verified SSH tunnel. Hermes terminal tools run with the host user's permissions; profile prompts do not prevent file access.

Review upstream code and model terms before installing. The downloader checks declared sizes and hashes; checksums do not certify safe code, rights or provenance beyond the recorded method. Do not enable arbitrary remote model code. Keep raw voice references, embeddings, keys and account sessions outside the Git repository.

Report a vulnerability through GitHub's **Report a vulnerability** / private reporting feature where available. If that feature is unavailable, use the public contact route at [Labverse](https://labverse.org) to request a private channel without sending secrets in the initial message. Do not post exploit credentials or private data in a public issue.

If you accidentally expose a credential, revoke/rotate it at its provider first. Removing a current file is insufficient once Git history, forks or caches contain the value.
