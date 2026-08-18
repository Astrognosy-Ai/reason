# reason:// protocol prototype (archived)

This repository preserves the original public `reason://` protocol and Xport
prototype. It is no longer the active SDK, MCP implementation, managed-service
source, or current integration guide.

## Use the current public project

[ReasonRDN](https://github.com/Astrognosy-Ai/ReasonRDN) is the canonical public
local-first memory, `reason://` addressing, CLI, SDK, and MCP project.

Current release at the time this repository was archived: **ReasonRDN 0.5.0**.

```bash
pip install "reason-rdn[mcp]==0.5.0"
codex mcp add reason-rdn -- rdn-mcp
```

- [ReasonRDN source and releases](https://github.com/Astrognosy-Ai/ReasonRDN)
- [ReasonRDN on PyPI](https://pypi.org/project/reason-rdn/)
- [Live Reason Registry](https://reason.astrognosy.com/)
- [Reason Registry API](https://reason.astrognosy.com/docs)
- [Live WARF Gateway](https://warf.astrognosy.com/)
- [Current reason:// Internet-Draft record](https://datatracker.ietf.org/doc/draft-westerbeck-reason-protocol/)

ReasonRDN keeps ordinary `remember`, `recall`, and default resolution local.
WARF arbitration, managed Registry admission, and network resolution are
separate explicit actions.

## Historical contents

The source, protocol text, namespace notes, and governance material in this
repository are retained unchanged as April 2026 lineage. They describe an
earlier automatic-promotion model and should not be used as current API or SDK
guidance.

This repository was superseded and archived in August 2026. Its Git history
remains available for provenance. New work belongs in ReasonRDN or the current
private service owners, not in this prototype.

License: CC BY 4.0
