---
title: reason:// — Web Agent Reasoning Federation (WARF)
abbrev: reason
docname: draft-jwesterbeck-reason-reasoning-artifact-federation-00
category: info
ipr: trust200902
date: 2026-03-27
area: ART
workgroup:
keyword: agent, reasoning, federation, privacy, arbitration, structural-centroid

author:
  -
    name: Jacob Westerbeck
    email: jacob@pcfic.com
    org: Astrognosy AI / Pacific Intelligence Concepts

normative:
  RFC2119:
  RFC8174:

informative:

---

# Abstract

This document defines reason://, a protocol and address space for sharing compressed structural reasoning artifacts between autonomous agents without transferring raw data, models, or sensitive records. Artifacts are admitted to the registry only after winning a live WARF (Web Agent Reasoning Federation) arbitration round. The protocol is designed for regulated domains (healthcare, finance, defense, pharma, aerospace) where data sharing is legally or architecturally prohibited.

# Introduction

Every AI agent today is a silo. Learned intelligence cannot cross institutional boundaries without violating privacy, IP, or classification rules. `reason://` provides the missing infrastructure layer: a public, DNS/HTTP-style address space for **non-invertible structural centroids** of reasoning patterns.

# Architecture

A reasoning artifact contains only:
- `pattern`: compressed structural centroid (mathematically non-invertible, r=0.0149 reconstruction error)
- Calibrated thresholds
- PCF/WARF arbitration score
- Provenance (no raw data field exists)

See the live reference implementation at https://warfdemo.streamlit.app (reason:// demo tab).

# Novelty

`reason://` is the first protocol to combine:
1. Structural centroids (shape of insight only)
2. Meritocratic registry gated by live competitive arbitration
3. Public reason:// address space
4. Architectural (not policy) privacy guarantee

It is distinct from MCP, A2A, ACP and all existing agent-messaging or federated-ML systems.

# Security Considerations

Privacy is architectural: the schema contains no field for raw data. Tokenized structural corpora are scored without exposing evidence.

# IANA Considerations

This document has no IANA actions.

# References

(Informative references to PCF, WARF, and related agent protocols will be added in -01.)

# Authors' Addresses

Jacob Westerbeck
Astrognosy AI / Pacific Intelligence Concepts
Email: jacob@pcfic.com
