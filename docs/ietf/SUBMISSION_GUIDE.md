# IETF Submission Guide — draft-jwesterbeck-reason-reasoning-artifact-federation

Step-by-step checklist for submitting the `reason://` Internet-Draft to the IETF datatracker.

---

## 1. Convert Markdown to XML

1. Go to [https://author-tools.ietf.org/](https://author-tools.ietf.org/)
2. Paste the contents of `draft-00.md` into the input field
3. Select **Markdown → XML** conversion
4. Download the resulting `.xml` file
5. Save it as `draft-jwesterbeck-reason-reasoning-artifact-federation-00.xml`

---

## 2. Run idnits validation

1. Go to [https://author-tools.ietf.org/idnits](https://author-tools.ietf.org/idnits)
2. Upload the `.xml` file from Step 1
3. Fix any errors or warnings flagged by idnits before proceeding
   - Common issues: missing boilerplate, malformed references, incorrect date format
4. Re-convert and re-validate until idnits reports clean

---

## 3. Submit to the IETF Datatracker

1. Go to [https://datatracker.ietf.org/submit/](https://datatracker.ietf.org/submit/)
2. Log in (or create an account at [https://datatracker.ietf.org/accounts/create/](https://datatracker.ietf.org/accounts/create/))
3. Upload the validated `.xml` file
4. Verify that the title and abstract auto-fill correctly:
   - **Title**: `reason:// — A URI Scheme and Protocol for Sharing Structural Reasoning Artifacts`
   - **Author**: `Jacob Westerbeck`
5. Complete the submission and confirm via the email sent to `jacob@pcfic.com`

---

## 4. After submission

1. Note the permanent Datatracker URL:
   `https://datatracker.ietf.org/doc/draft-jwesterbeck-reason-reasoning-artifact-federation/`
2. Update the `reason/` GitHub README with the Datatracker link
3. Update the `docs/ietf/draft-00.md` header to reflect the actual submission date

---

## Draft file

The full Internet-Draft is at [`draft-00.md`](draft-00.md).

Draft name: `draft-jwesterbeck-reason-reasoning-artifact-federation-00`

---

## Key contacts for feedback

Post-submission, relevant IETF communities for feedback include:

- **ART area** (Applications and Real-Time) — primary area for URI scheme registration
- **dispatch mailing list** — for new work items without an existing WG home
- **URI review list** — for IANA URI scheme registration review

IANA request for the `reason` URI scheme is included in Section 8 of the draft.
