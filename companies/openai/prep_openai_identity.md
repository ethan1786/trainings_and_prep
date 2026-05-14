# OpenAI — Software Engineer, Identity Infrastructure Engineering

> **Prep doc.** Role: SWE, Identity Infrastructure Engineering (IT team).
> Comp: $184K–$385K + equity. Location: hybrid (SF/Seattle/NYC) or possibly remote.
> Status: HR intro call scheduled May 15. Actual interviews TBD (after Coinbase VO).
> Last updated: May 14, 2026

---

## Role Analysis — What They Actually Want

### Team Context
- Sits under **IT** (not the Security team — that's the InfraSec role you also applied to)
- Partners with: Applied Engineering, Research, IT, Security
- Builds IAM for internal use — protecting model weights, customer data, critical systems
- **Multi-cloud**: AWS + Azure + GCP simultaneously
- This is an INTERNAL PLATFORM team — they build and OPERATE the IAM (unlike HashiCorp which ships products others run)

### Three Focus Areas (from JD)

| Area | What They Build | Your Experience |
|---|---|---|
| **Identity & Access Orchestration** | User + service identity, fine-grained access controls consistent across cloud providers | Keycloak SSO, RBAC at Kong gateway, JWT validation, mTLS service-to-service |
| **Multi-Cloud Security** | Protect model weights + customer data across AWS/Azure/GCP | AWS deep (ECS/EKS/IAM), multi-cloud is growth area |
| **Automation & Tooling** | Frameworks, APIs, CLI tools for provisioning + credential rotation | Terraform automation, built auth plugins, built tooling from scratch at Toast |

### What Makes This Different from HashiCorp

| | HashiCorp | OpenAI Identity |
|---|---|---|
| Customer | External companies (self-host) | Internal teams (researchers, engineers) |
| Operate it? | No — customers run it | **Yes — you run it in production** |
| On-call relevant? | Less so | **Yes — protecting live model weights** |
| Security bar | "Ship correct binaries" | "Prevent unauthorized access to $B in AI models" |
| Language | Go | **Python/Go** (not Java) |
| Collaboration | Other platform engineers | **Researchers + compliance + applied eng** |

**Key insight:** Operational excellence IS a talking point here (unlike HashiCorp). They build AND operate. If someone gets unauthorized access to model weights, that's a catastrophic incident.

---

## Gaps to Address

| Gap | How to Frame |
|---|---|
| **Auth work is 7 years old** | "I built it at Applause AND I've been consuming IAM infrastructure daily for 6 years. I know what works and what's frustrating from the user side." |
| **Python/Go not primary language** | "I wrote Kong RBAC plugins in Python. My primary is Java but I pick up languages fast — the auth/IAM domain knowledge is what's hard to learn, not syntax." |
| **Multi-cloud (only deep in AWS)** | "I'm deep in AWS. The IAM concepts (roles, policies, federation, cross-account access) are the same across clouds — the API surface is different but the mental model transfers." |
| **No threat modeling experience explicitly** | "When I designed the auth migration at Applause, I thought about: what if the legacy system is compromised during dual-auth? What if token validation is bypassed? What are the failure modes that expose user data? That's threat modeling in practice." |

---

## Your Angle — Why You Fit

> "I've built production IAM infrastructure — Keycloak SSO, OAuth/SAML federation, custom RBAC enforcement at the API gateway, mTLS for zero-trust service communication. I've also been a CONSUMER of IAM for 6 years — managing AWS IAM roles, Terraform-provisioned permissions, service-to-service auth. And recently I've been building AI platform infrastructure (MCP servers) — so I understand the AI workload context your IAM needs to protect. That combination — builder + consumer + AI context — is rare."

### The Three-Part Story

| Phase | Experience | Signal |
|---|---|---|
| **I built IAM** | Applause: Keycloak SSO, Kong RBAC, mTLS, dual-auth migration | "I can build identity systems from scratch" |
| **I consumed IAM** | CarGurus: AWS IAM, Terraform, service-to-service auth daily | "I know what good IAM feels like to users" |
| **I understand AI workloads** | MCP server, agent backends, AI platform infrastructure | "I know what you're protecting and who your consumers are" |

---

## HR Intro Call Prep (May 15)

### Questions They'll Ask

**"Tell me about yourself."**
> "Staff/Principal backend engineer, 13 years. Most relevant: at Applause I built a production IAM platform — Keycloak SSO with OAuth/SAML federation, custom RBAC enforcement at the Kong API gateway, service mesh with mTLS. At CarGurus I've been the platform technical lead for 6 years — distributed systems, API design, and most recently AI platform infrastructure (MCP servers for ChatGPT integration). I bring both the builder AND consumer perspective on identity infrastructure."

**"Why this role / why OpenAI?"**
> "Two things. First, identity infrastructure is where my deepest experience maps — I've built IAM from scratch and I've depended on IAM daily as a platform engineer. I want to go back to building it, at a company where the stakes are highest. Second, protecting AI model weights and research data is genuinely a new class of problem — the assets are uniquely valuable and the threat model is different from traditional web apps. That's interesting to me."

**"Why are you leaving your current role?"**
> "I want vertical technical depth on security infrastructure. I've been doing broad platform work — touching many systems, many teams. I want to own one critical domain deeply and make it excellent. Identity infrastructure at OpenAI is exactly that."

### Questions to Ask on Intro Call

**Clarify level/fit:**
- What level is this role targeting? The comp range is wide — is this Senior, Staff, or both?
- Is remote truly an option for this role, or is hybrid strongly preferred?

**Clarify team/scope:**
- How big is the Identity Infrastructure Engineering team today?
- Is the team building from scratch, or extending an existing IAM platform?
- What's the current identity stack? (Okta? Custom? Cloud-native IAM?)

**Clarify process:**
- What does the full interview process look like for this role?
- What's the timeline you're looking to fill by?

**Show interest:**
- What are the biggest identity challenges unique to AI research environments? (e.g., ephemeral GPU cluster access, model weight access control)
- How does the team work with research engineers who may not want to think about auth?

---

## Technical Depth to Have Ready (for later rounds)

### Identity Concepts You Should Know

| Concept | What It Is | Your Experience |
|---|---|---|
| **OIDC (OpenID Connect)** | Identity layer on top of OAuth 2.0. Issues ID tokens (JWT) proving who the user is. | Used via Keycloak — issued OIDC tokens for SSO |
| **OAuth 2.0 flows** | Authorization framework. Client credentials (service-to-service), auth code (user login), device flow. | Implemented multiple flows at Applause |
| **SAML** | XML-based federation for enterprise SSO. Older but still used for corporate IdP integration. | Configured SAML federation in Keycloak |
| **SPIFFE/SPIRE** | Service identity framework — cryptographic identity for workloads, not just users. Industry standard for zero-trust. | Didn't use directly, but mTLS with Linkerd is the same principle |
| **Policy as code** | Define access policies in code (OPA/Rego, Cedar, Sentinel). Version, test, review like any other code. | Conceptually — RBAC rules were code-defined in Kong plugins |
| **Dynamic credentials** | Short-lived, programmatically issued credentials. Never static secrets. | Keycloak token rotation, short-lived JWTs |
| **Cross-account / cross-cloud federation** | One identity system trusts another. AWS assume-role, GCP workload identity federation. | AWS cross-account assume-role in Terraform |
| **Service mesh identity** | mTLS certificates as workload identity. Every service proves who it is cryptographically. | Linkerd + mTLS deployment at Applause |

### Multi-Cloud IAM Comparison (good to know)

| Concept | AWS | Azure | GCP |
|---|---|---|---|
| Service identity | IAM Roles + Instance Profiles | Managed Identity | Service Accounts |
| Cross-account trust | AssumeRole + trust policies | Tenant/subscription federation | Workload Identity Federation |
| Policy language | JSON policies | Azure RBAC + Conditional Access | IAM policies (JSON) |
| Secret management | Secrets Manager / Parameter Store | Key Vault | Secret Manager |
| Federation | SAML/OIDC Identity Providers | Azure AD / Entra ID | Workload Identity |

### AI-Specific Identity Challenges (differentiator)

- **Model weight access**: Who can download/copy weights? How do you audit access to multi-billion-dollar assets?
- **Ephemeral GPU clusters**: Workloads spin up for hours then disappear. How do you issue and revoke identity for transient compute?
- **Researcher access**: Research engineers want minimal friction. How do you balance "let me experiment freely" with "don't leak model weights"?
- **Multi-team data isolation**: Applied team data vs Research team data vs Customer data — same infrastructure, different access boundaries.
- **Agent-to-agent auth**: AI agents calling APIs on behalf of users — what identity does the agent have? How do you scope its permissions?

---

## Competitive Positioning

**Why OpenAI might prefer you over a pure security engineer:**
- You understand the AI workload context (MCP, agent architectures, model serving)
- You've been a PLATFORM CONSUMER — you know what researchers/engineers hate about auth systems
- You've built full-stack IAM (not just configured Okta)
- You've operated infrastructure in production (SLOs, on-call, incident response)

**Why they might hesitate:**
- Auth work is 2017-2019 (7 years ago)
- Primary language is Java, not Python/Go
- No formal security background (no certs, no dedicated security team experience)
- Multi-cloud depth is limited to AWS

**Counter each hesitation on the call:**
- "The domain knowledge doesn't expire — OAuth, SAML, OIDC, RBAC are the same. What's changed is the tooling, not the concepts."
- "Python is my secondary language (wrote Kong plugins). Languages are learnable; identity domain expertise isn't."
- "My security thinking is applied, not academic — I think about failure modes, unauthorized access paths, and how to migrate without breaking trust."
- "AWS deep, multi-cloud principles transfer. I learn cloud APIs fast."

---

## Timeline Strategy

1. **May 15:** HR intro call — clarify level, remote, process
2. **May 19-20:** Coinbase VO (priority)
3. **After Coinbase:** Schedule OpenAI technical rounds
4. **Ideal:** Have OpenAI progressing while waiting for Coinbase decision — creates leverage
