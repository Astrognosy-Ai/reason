# reason:// — Reasoning Infrastructure for the Agentic Internet

**The HTTP for learned intelligence.**
Share *structural reasoning patterns* across silos — without sharing data, models, or weights.

- **Privacy**: Architecturally guaranteed (non-invertible centroids, r=0.0149 reconstruction bound)
- **Trust**: Only validated winners via live WARF arbitration
- **One line**: `artifact = reason.resolve("reason://medicine/records/longitudinal-maintenance-prediction")`

**Status**: v0.1 (Bootstrap) — Spec + SDK + Reference Node live.

## Try it live right now
**[Open the reason:// Demo tab →](https://warfdemo.streamlit.app)**
Deposit a structural artifact → resolve it from another agent → watch the privacy guarantee in action.

## Quickstart (Python)
```bash
pip install reason-py
from reason import ReasonClient
client = ReasonClient()
artifact = client.resolve("reason://finance/fraud/synthetic-identity-temporal-motif")
score = client.compare(my_embedding, artifact)
See examples/ for hospital, bank fraud, defense, and pharma use cases.
Open Protocol: CC BY 4.0 (this repo)
Commercial Engine: Pacific platform (self-hosted WARF nodes, certified artifacts, production scale) — pcfic.com
Governance: Bootstrap by Astrognosy → IETF transition (see GOVERNANCE.md)
Built by: Astrognosy AI / Pacific Intelligence Concepts
Tadaaqaa.
text**reason/LICENSE**
```text
Creative Commons Attribution 4.0 International (CC BY 4.0)

Full license: https://creativecommons.org/licenses/by/4.0/

You are free to share and adapt this protocol specification and reference implementation
as long as you give appropriate credit to Astrognosy AI / Pacific Intelligence Concepts.
