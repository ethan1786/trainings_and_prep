# HM Interview — HashiCorp/IBM (May 13, 1 hr, video)

**Format:** HM video interview — conversational/behavioral. First technical-ish call after HR screen.
**Role:** Staff SWE, HashiCorp Secure (Vault/Boundary)
**Context:** HashiCorp acquired by IBM. Team builds security infrastructure products (secrets management, access management).

---

## What They're Likely Evaluating

- Can you operate at Staff level in a security infrastructure team?
- Do you have relevant domain experience (auth, identity, secrets, access control)?
- Are you a good culture fit for a distributed, document-driven team?
- Can you collaborate across teams on infrastructure that other engineers depend on?

---

## Your Angle — Why You're a Fit

> "I've built production IAM infrastructure — Keycloak SSO, OAuth 2.0/SAML federation, custom RBAC enforcement at the API gateway, service mesh with mTLS. I understand what it takes to build security infrastructure that other teams depend on. I also use Terraform daily, so I know the HashiCorp ecosystem from the consumer side."

---

## Their Focus → Your Story

| What They Probe | Your Answer | Key Detail |
|---|---|---|
| Auth/security experience | Story 11 (Applause — Keycloak, Kong, mTLS, service mesh) | Built production IAM platform from scratch |
| Platform/infra mindset | Story 1 (API Mod — built infrastructure 10+ teams depend on) | Platform thinking, not one-off solutions |
| Cross-team collaboration | Story 1 (influence layer — RFCs, pre-socialization, consensus) | Document-driven, async culture (matches HashiCorp) |
| Ownership / end-to-end | Story 13 (Toast — built infra nobody assigned) | Self-directed, sees what needs building |
| Disagree and commit | Story 8 (GraphQL — lost argument, committed, helped succeed) | Mature, not ego-driven |
| Failure / learning | Story 14 (Mongo — peak traffic, connection starvation) | Learned to design for operational reality |

---

## Direct Questions — HashiCorp Specific

**"Tell me about yourself."**
> "Staff/Principal backend engineer, 13 years. Three chapters: early engineer at Toast building everything from scratch. Then Applause where I led auth modernization — Keycloak SSO, API gateway security, service mesh with mTLS. For the last 6 years at CarGurus I've been the platform technical lead — redesigned the highest-traffic API, drove architecture standards across 10+ teams, and most recently building AI platform infrastructure. My auth and platform background maps directly to Vault and Boundary."

**"Why HashiCorp/IBM?"**
> "Two reasons. First, I use Terraform daily — I know the HashiCorp ecosystem from the consumer side and I'm excited to work on the producer side. Second, my auth background — Keycloak, Kong, service mesh, mTLS — maps directly to what Vault and Boundary do. IBM's backing gives the team stability to invest long-term in the platform. I want to build security infrastructure at scale."

**"Why are you leaving?"**
> "I've been at CarGurus 6 years, led the biggest initiatives, set the architecture standards. But I've outgrown the problems. Security infrastructure at HashiCorp's scale — used by thousands of companies — is a different level of challenge and impact."

**"What do you know about Vault/Boundary?"**
> "Vault: secrets management — dynamic secrets, encryption as a service, PKI/certificate management. The key insight is that secrets should be short-lived and programmatically issued, not long-lived and manually rotated. Boundary: secure access to infrastructure without exposing the network — identity-based access rather than network-based (VPN replacement). Both fit the zero-trust model: verify identity at every layer, never trust the network."

---

## Questions to Ask

**About the team:**
- What does the team look like today? How many engineers on Vault vs. Boundary?
- How does the team work day-to-day — document-driven? RFCs? What's the collaboration model?
- What's the biggest technical challenge the Secure team is facing right now?

**About the role:**
- What would success look like in the first 6 months for this role?
- What's the balance between feature development vs. reliability/platform work?
- How does the IBM acquisition affect the team's autonomy and roadmap?

**About the tech:**
- What's the tech stack? (I know Vault is Go — what else?)
- How do you handle backward compatibility with thousands of users depending on your APIs?
- What's the deployment model — how do you ship changes to a security product safely?

**About growth:**
- What does Staff level look like at HashiCorp? How is it different from Senior in practice?
- How do you see the Secure product evolving over the next 2 years?

---

## Things to Mention Proactively

- **Terraform daily user** — "I'm a consumer of your ecosystem, so I understand what your users need"
- **Document-driven culture** — "I drive decisions through RFCs and design docs, which I understand is how HashiCorp operates"
- **Auth depth** — Keycloak, OAuth 2.0, SAML, JWT validation, RBAC, mTLS, service mesh — this isn't surface knowledge
- **Platform builder** — "I build infrastructure other teams depend on. That's what Vault/Boundary is."

---

## Things to NOT Do

- Don't oversell AI/MCP stuff (not relevant to this role)
- Don't lead with CarGurus API modernization (lead with Applause auth story instead — more relevant)
- Don't ask about comp/timeline yet (save for after)
- Don't badmouth the IBM acquisition — frame it positively ("stability to invest long-term")

---

## Tone

This is a mutual fit conversation. You want to know: is this team autonomous post-acquisition? Is the role actually Staff-scope? Is the work interesting (building security infra used by thousands)? Ask questions that reveal the reality behind the job posting.
