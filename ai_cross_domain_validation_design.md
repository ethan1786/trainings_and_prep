# AI-Powered Cross-Domain Validation — Technical Design

> Design doc for Story 19. Three phases, each independently valuable.
> Status: Design phase. Use in interviews as "current initiative I'm driving."

---

## Problem

The VDP (Vehicle Detail Page) is CarGurus' most critical page. Three teams work on it:

| Team | Domain | Examples |
|---|---|---|
| Core Platform | US-centric features, shared components | Pricing, lead capture, inventory display |
| International | CA/UK locale-specific features | Tax formatting, legal disclaimers, currency, metric units |
| Mobile | React Native, mobile-only features | Compact layouts, touch interactions, mobile-specific APIs |

**Current validation process:**
1. Team A ships a feature
2. Team A manually notifies Teams B and C
3. Teams B and C manually test their domains against the change
4. Back-and-forth for 2-5 days if issues are found
5. Repeat for every feature release

**Problems:** Slow (days), manual (error-prone), doesn't scale, depends on tribal knowledge of domain boundaries.

---

## Phase 1: AI Impact Analysis (on PR)

### What It Does
When a PR is opened touching VDP code, an AI agent analyzes the diff and produces an impact report identifying which domains and teams are affected.

### Architecture

```
Developer opens PR
        │
        ▼
┌─────────────────────┐
│  GitHub Webhook      │ ── triggers on PR open/update
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Impact Analyzer     │ ── serverless function (Lambda or ECS task)
│  (LLM-powered)      │
└────────┬────────────┘
         │  reads:
         │  1. PR diff (via GitHub API)
         │  2. Domain boundary config (YAML)
         │  3. Historical impact data (optional)
         │
         ▼
┌─────────────────────┐
│  Impact Report       │ ── posted as PR comment
│  + Auto-tag teams    │ ── adds GitHub labels / reviewers
└─────────────────────┘
```

### Domain Boundary Config

```yaml
# .github/domain-boundaries.yml
domains:
  international:
    owners: ["@intl-team"]
    paths:
      - "src/components/vdp/locale/**"
      - "src/components/vdp/pricing/formatters/**"
      - "src/i18n/**"
    keywords:
      - "locale", "currency", "tax", "CAD", "GBP", "metric"
    api_contracts:
      - "api/specs/pricing-intl.yaml"
      - "api/specs/tax-calculation.yaml"

  mobile:
    owners: ["@mobile-team"]
    paths:
      - "src/components/vdp/mobile/**"
      - "src/native/**"
    keywords:
      - "viewport", "touch", "compact", "react-native", "mobile"
    api_contracts:
      - "api/specs/vdp-mobile.yaml"

  core:
    owners: ["@core-platform"]
    paths:
      - "src/components/vdp/**"
    api_contracts:
      - "api/specs/vdp-core.yaml"
      - "api/specs/inventory.yaml"
```

### LLM Prompt Strategy

The analyzer uses a two-stage approach:

**Stage 1 — Rule-based pre-filter (fast, cheap, no LLM):**
- Check if changed file paths match any domain's `paths` patterns
- Check if diff contains any domain's `keywords`
- If no domain matches, skip LLM call entirely (most PRs won't touch cross-domain code)

**Stage 2 — LLM semantic analysis (only when pre-filter flags potential impact):**

```
System: You are a code impact analyzer for a multi-team web application.
Given a code diff and domain boundary definitions, identify which domains
are affected and explain why.

Rules:
- A domain is "directly affected" if the diff modifies files in its paths
- A domain is "indirectly affected" if the diff changes shared interfaces,
  data models, API contracts, or rendering logic that the domain depends on
- Be specific: name the exact files, functions, or data fields that create
  the cross-domain dependency
- Rate confidence: HIGH (direct path/contract change), MEDIUM (shared
  interface change), LOW (semantic similarity, may not actually affect)

Input:
- Diff: {diff}
- Domain boundaries: {domain_config}
- Changed files: {file_list}

Output JSON:
{
  "affected_domains": [
    {
      "domain": "international",
      "confidence": "HIGH",
      "reason": "PR modifies priceFormatted field in PricingComponent — intl
                 team's CA pricing formatter reads this field",
      "affected_files": ["src/components/vdp/pricing/PricingComponent.tsx"],
      "suggested_reviewers": ["@intl-team"]
    }
  ],
  "no_cross_domain_impact": false,
  "summary": "This PR affects international pricing display. CA and UK
              locale formatters depend on the priceFormatted field being renamed."
}
```

### Output: PR Comment

```markdown
## 🔍 Cross-Domain Impact Analysis

**Affected domains:**

| Domain | Confidence | Reason |
|---|---|---|
| International | 🔴 HIGH | `priceFormatted` field renamed — CA/UK formatters depend on this |
| Mobile | 🟡 MEDIUM | `PricingComponent` layout changed — may affect compact mobile view |

**Suggested reviewers:** @intl-team, @mobile-team

**Suggested test scenarios:**
- [ ] Verify CA locale pricing display with new field name
- [ ] Verify UK locale pricing display with new field name
- [ ] Verify mobile compact pricing view renders correctly

---
*Auto-generated by AI Impact Analyzer. Config: `.github/domain-boundaries.yml`*
```

### Cost & Latency
- Pre-filter: <100ms, zero cost
- LLM call (when needed): ~2-5 seconds, ~$0.01-0.05 per PR (GPT-4o or Claude Haiku for cost efficiency)
- Most PRs won't trigger the LLM call — the pre-filter handles single-domain changes

### Key Design Decisions
- **YAML config over hardcoded rules** — teams can update their own domain boundaries via PR
- **Two-stage (rules + LLM)** — avoid LLM cost for the 80% of PRs that are single-domain
- **Confidence levels** — don't cry wolf on every PR; HIGH = must review, LOW = FYI
- **Posted as PR comment, not blocking** — Phase 1 is advisory; Phase 2 makes it blocking

---

## Phase 2: MCP Server for Cross-Domain Spec Validation

### What It Does
An MCP server that exposes tools for reading and cross-referencing API contracts, component specs, and data models across domains. Integrates into CI to block PRs with breaking cross-domain changes.

### Architecture

```
CI Pipeline (on PR)
        │
        ▼
┌─────────────────────┐
│  Spec Validator      │ ── CI job (runs after build)
│  (MCP Client)        │
└────────┬────────────┘
         │  calls MCP tools:
         │  1. read_api_spec(domain, service)
         │  2. diff_contracts(old_spec, new_spec)
         │  3. check_consumers(changed_field)
         │  4. validate_compatibility(change, consumer_specs)
         │
         ▼
┌─────────────────────┐
│  MCP Server          │ ── runs as sidecar or remote service
│  (Java / your stack) │
└────────┬────────────┘
         │  has access to:
         │  - OpenAPI / GraphQL specs per domain
         │  - Component prop type definitions
         │  - Shared data model schemas
         │  - Consumer registry (who reads what)
         │
         ▼
┌─────────────────────┐
│  Validation Result   │ ── pass/fail + details
│  → CI gate           │ ── blocks merge if breaking
│  → PR comment        │ ── explains what broke
└─────────────────────┘
```

### MCP Tools

```java
@Tool("read_api_spec")
// Reads an OpenAPI or GraphQL spec for a given domain and service
// Returns: parsed spec object with endpoints, fields, types
SpecResult readApiSpec(String domain, String serviceName)

@Tool("diff_contracts")
// Compares two versions of a spec (base branch vs PR branch)
// Returns: list of added/removed/modified fields with breaking change flags
ContractDiff diffContracts(String specPath, String baseBranch, String prBranch)

@Tool("check_consumers")
// Given a changed field/endpoint, finds all consumers across domains
// Uses consumer registry: which domains read which fields
// Returns: list of consuming domains, components, and their expected types
ConsumerList checkConsumers(String changedField, String sourceService)

@Tool("validate_compatibility")
// Given a contract diff and list of consumers, checks if the change is safe
// Rules:
//   - Removing a field that a consumer reads → BREAKING
//   - Renaming a field without alias → BREAKING
//   - Changing a field type → BREAKING
//   - Adding a new optional field → SAFE
//   - Adding a required field to a request → BREAKING for consumers
ValidationResult validateCompatibility(ContractDiff diff, ConsumerList consumers)
```

### Consumer Registry

The key data structure — who reads what:

```yaml
# consumer-registry.yml
consumers:
  - domain: "international"
    service: "ca-pricing-formatter"
    reads_from:
      - source: "core/pricing-api"
        fields: ["priceFormatted", "currency", "taxAmount", "taxRate"]
      - source: "core/inventory-api"
        fields: ["stockStatus", "deliveryEstimate"]

  - domain: "mobile"
    service: "mobile-vdp-bff"
    reads_from:
      - source: "core/pricing-api"
        fields: ["priceFormatted", "currency", "monthlyPayment"]
      - source: "core/vdp-api"
        fields: ["title", "imageUrls", "sellerName", "distance"]
```

### CI Integration

```yaml
# .github/workflows/cross-domain-validation.yml
cross-domain-check:
  runs-on: ubuntu-latest
  steps:
    - name: Detect changed specs
      run: |
        git diff origin/main --name-only | grep -E '\.(yaml|graphql|proto)$' > changed_specs.txt

    - name: Run MCP spec validator
      if: steps.detect.outputs.has_spec_changes == 'true'
      run: |
        java -jar spec-validator.jar \
          --mcp-server-url $MCP_SERVER_URL \
          --changed-specs changed_specs.txt \
          --consumer-registry consumer-registry.yml \
          --base-branch origin/main \
          --pr-branch ${{ github.head_ref }}

    - name: Post results
      if: failure()
      uses: actions/github-script@v6
      with:
        script: |
          // Post breaking change details as PR comment
          // Block merge
```

### Validation Output Example

```
❌ BREAKING CHANGE DETECTED

Change: core/pricing-api field `priceFormatted` renamed to `displayPrice`

Affected consumers:
  1. international/ca-pricing-formatter
     - Reads `priceFormatted` for CA locale formatting
     - Will break: field no longer exists
     
  2. mobile/mobile-vdp-bff
     - Reads `priceFormatted` for compact price display
     - Will break: field no longer exists

Suggested fix:
  Option A: Keep `priceFormatted` as alias (non-breaking)
  Option B: Update consumer specs in intl and mobile domains first
```

### How This Extends Your Parity Testing Pattern

| Parity Testing (Story 2) | Spec Validation (This) |
|---|---|
| Compares old vs new **responses** | Compares old vs new **contracts** |
| At runtime, 50% production traffic | At build time, in CI |
| Catches functional regressions | Catches interface regressions |
| Single service, two versions | Multiple domains, one change |

Same principle: automated comparison of two sources of truth with divergence alerting. Applied earlier in the pipeline (shift-left).

---

## Phase 3: AI-Generated Cross-Domain Test Suites

### What It Does
Given a code change and its impact analysis (Phase 1), AI generates and runs test scenarios across all affected domains.

### Architecture

```
Phase 1 Impact Report
        │ (knows which domains are affected)
        ▼
┌─────────────────────┐
│  Test Generator      │ ── LLM generates test scenarios per domain
│  (LLM-powered)      │
└────────┬────────────┘
         │  generates:
         │  - Test scenarios (natural language)
         │  - Test code (Playwright/Cypress for UI, REST for API)
         │  - Expected behavior per domain variant
         │
         ▼
┌─────────────────────┐
│  Cross-Domain        │ ── runs tests against staging
│  Test Runner         │ ── parallel execution per domain variant
└────────┬────────────┘
         │  runs against:
         │  - US locale (default)
         │  - CA locale (international)
         │  - UK locale (international)
         │  - Mobile viewport (375px)
         │  - Desktop viewport (1440px)
         │
         ▼
┌─────────────────────┐
│  Result Comparator   │ ── compares results across domains
│  (Parity Engine)     │ ── flags unexpected differences
└─────────────────────┘
```

### Test Generation Prompt

```
System: You are a test engineer for a multi-domain web application.
Given a code change and its cross-domain impact analysis, generate
test scenarios that verify correctness across all affected domains.

Rules:
- Generate ONE test scenario per affected domain interaction
- Each test must check the specific field/component the impact
  analysis identified
- Include expected behavior for EACH domain variant (US, CA, UK, mobile)
- Flag where behavior SHOULD differ (locale-specific) vs SHOULD NOT
  differ (regression)

Input:
- Code change: {diff_summary}
- Impact analysis: {phase_1_output}
- Domain specs: {relevant_specs}

Output:
[
  {
    "scenario": "Verify pricing display after priceFormatted rename",
    "affected_domains": ["international", "mobile"],
    "test_steps": [
      "Navigate to VDP for vehicle ID 12345",
      "Assert pricing component renders correctly"
    ],
    "expected_by_variant": {
      "US_desktop": "Price shows as '$25,000'",
      "CA_desktop": "Price shows as 'CA$32,000' with tax breakdown",
      "UK_desktop": "Price shows as '£19,500' with VAT",
      "US_mobile": "Price shows as '$25,000' in compact format",
      "CA_mobile": "Price shows as 'CA$32,000' in compact format"
    },
    "regression_if": "Any variant shows raw field name, empty price, or error"
  }
]
```

### Result Comparison (Parity Engine)

The comparator applies the same structural diff logic as Story 2's parity testing, but across domain variants instead of old-vs-new:

```java
class CrossDomainComparator {

    ComparisonResult compare(Map<String, TestResult> variantResults) {
        List<Divergence> divergences = new ArrayList<>();

        for (var pair : allPairs(variantResults)) {
            StructuralDiff diff = deepDiff(pair.left().response, pair.right().response);

            for (FieldDiff fd : diff.differences()) {
                if (isExpectedLocaleDifference(fd, pair.left().variant, pair.right().variant)) {
                    // CA showing CAD and US showing USD is expected — skip
                    continue;
                }
                // Unexpected difference — flag as potential regression
                divergences.add(new Divergence(fd, pair.left().variant, pair.right().variant));
            }
        }
        return new ComparisonResult(divergences);
    }
}
```

### Key Distinction: Expected vs Unexpected Differences

| Difference Type | Example | Action |
|---|---|---|
| **Expected locale difference** | US shows "$25,000", CA shows "CA$32,000" | Skip — this is correct |
| **Expected mobile difference** | Desktop shows full gallery, mobile shows single image | Skip — responsive design |
| **Unexpected difference** | CA shows empty price, US shows correct price | 🔴 Flag as regression |
| **Unexpected consistency** | UK shows "$" instead of "£" after a change | 🔴 Flag — locale not applied |

The "expected difference" rules come from the domain boundary config (Phase 1) — the system knows what *should* differ across variants.

---

## Implementation Roadmap

| Phase | Effort | Value | Dependency |
|---|---|---|---|
| **Phase 1: Impact Analysis** | 1-2 weeks | High — immediate coordination savings | GitHub API, LLM API, domain config YAML |
| **Phase 2: Spec Validation** | 3-4 weeks | High — catches breaking changes in CI | MCP server, consumer registry, CI integration |
| **Phase 3: Test Generation** | 4-6 weeks | Medium-high — automated regression detection | Phase 1 output, staging environment, test runner |

Each phase is independently valuable. Phase 1 alone saves days of manual coordination.

---

## Interview Talking Points

- **Builds on prior work:** MCP server (Story 3) + parity testing (Story 2) = this initiative
- **Shift-left philosophy:** Catch cross-domain issues at PR time, not in staging or production
- **AI as infrastructure, not gimmick:** The LLM does semantic analysis humans can't scale; the rules engine does structural validation that's deterministic
- **Incremental delivery:** Each phase ships independently and adds value — not a big-bang project
- **Coinbase connection:** "This is the same problem you'd face with payment rails, compliance, and risk teams all touching shared financial pipelines. How do you validate that a change to the ledger doesn't break the compliance team's reconciliation?"
