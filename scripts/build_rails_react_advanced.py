#!/usr/bin/env python3
"""Build feature-by-feature Rails + React Advanced curriculum with verified reading links."""

from __future__ import annotations

import argparse
import html
import socket
import subprocess
from datetime import date
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
TRACK_DIR = ROOT / "Rails and React"
HTML_PATH = TRACK_DIR / "ILA_Rails_React_Curriculum_Advanced.html"
PDF_PATH = TRACK_DIR / "ILA_Rails_React_Curriculum_Advanced.pdf"

UA = "Mozilla/5.0 (compatible; ILA-Curriculum-LinkChecker/1.0)"


COURSE = {
    "title": "ILA Rails and React Engineering Certification - Level 2",
    "subtitle": (
        "Feature-by-feature build of an ad bidding platform. "
        "Each chapter explains one feature and advances it step by step."
    ),
    "completion_window": "4-5 weeks",
    "chapters": 18,
    "track": "Rails API + React operator console",
    "certification": "Level 2, Mentor-reviewed",
    "journey": [
        "Phase 1: Build secure platform foundations.",
        "Phase 2: Deliver the bidding and revenue core.",
        "Phase 3: Ship high-velocity operator UX.",
        "Phase 4: Harden for reliability and launch.",
    ],
}


LINKS: dict[str, tuple[str, str]] = {
    "rails_getting_started": ("Rails Guides: Getting Started", "https://guides.rubyonrails.org/getting_started.html"),
    "rails_api_mode": ("Rails Guides: API Applications", "https://guides.rubyonrails.org/api_app.html"),
    "rails_routing": ("Rails Guides: Routing", "https://guides.rubyonrails.org/routing.html"),
    "rails_models": ("Rails Guides: Active Record Basics", "https://guides.rubyonrails.org/active_record_basics.html"),
    "rails_associations": ("Rails Guides: Associations", "https://guides.rubyonrails.org/association_basics.html"),
    "rails_validations": (
        "Rails Guides: Active Record Validations",
        "https://guides.rubyonrails.org/active_record_validations.html",
    ),
    "rails_migrations": ("Rails Guides: Active Record Migrations", "https://guides.rubyonrails.org/active_record_migrations.html"),
    "rails_querying": ("Rails Guides: Active Record Querying", "https://guides.rubyonrails.org/active_record_querying.html"),
    "rails_controller": ("Rails Guides: Action Controller Overview", "https://guides.rubyonrails.org/action_controller_overview.html"),
    "rails_active_job": ("Rails Guides: Active Job Basics", "https://guides.rubyonrails.org/active_job_basics.html"),
    "rails_security": ("Rails Guides: Security", "https://guides.rubyonrails.org/security.html"),
    "rails_testing": ("Rails Guides: Testing", "https://guides.rubyonrails.org/testing.html"),
    "rails_caching": ("Rails Guides: Caching with Rails", "https://guides.rubyonrails.org/caching_with_rails.html"),
    "rails_active_storage": ("Rails Guides: Active Storage", "https://guides.rubyonrails.org/active_storage_overview.html"),
    "react_learn": ("React Docs: Learn React", "https://react.dev/learn"),
    "react_state": ("React Docs: Managing State", "https://react.dev/learn/managing-state"),
    "react_thinking": ("React Docs: Thinking in React", "https://react.dev/learn/thinking-in-react"),
    "react_router": ("React Router: Tutorial", "https://reactrouter.com/en/main/start/tutorial"),
    "redux_essentials": (
        "Redux Toolkit: Essentials Tutorial",
        "https://redux.js.org/tutorials/essentials/part-1-overview-concepts",
    ),
    "tanstack_query": (
        "TanStack Query: React Overview",
        "https://tanstack.com/query/latest/docs/framework/react/overview",
    ),
    "postgres_indexes": ("PostgreSQL Docs: Indexes", "https://www.postgresql.org/docs/current/indexes.html"),
    "postgres_explain": ("PostgreSQL Docs: Using EXPLAIN", "https://www.postgresql.org/docs/current/using-explain.html"),
    "postgres_isolation": (
        "PostgreSQL Docs: Transaction Isolation",
        "https://www.postgresql.org/docs/current/transaction-iso.html",
    ),
    "postgres_mv": (
        "PostgreSQL Docs: Materialized Views",
        "https://www.postgresql.org/docs/current/rules-materializedviews.html",
    ),
    "sidekiq_best_practices": ("Sidekiq Wiki: Best Practices", "https://github.com/sidekiq/sidekiq/wiki/Best-Practices"),
    "owasp_top10": ("OWASP Top 10", "https://owasp.org/www-project-top-ten/"),
    "owasp_input_validation": (
        "OWASP Cheat Sheet: Input Validation",
        "https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html",
    ),
    "jwt_intro": ("JWT.io: Introduction", "https://jwt.io/introduction"),
    "docker_compose": ("Docker Docs: Compose Overview", "https://docs.docker.com/compose/"),
    "redis_docs": ("Redis Docs", "https://redis.io/docs/latest/"),
    "stripe_idempotency": ("Stripe Docs: Idempotent Requests", "https://docs.stripe.com/api/idempotent_requests"),
    "stripe_billing": ("Stripe Docs: Billing", "https://docs.stripe.com/billing"),
    "opentelemetry": ("OpenTelemetry Docs", "https://opentelemetry.io/docs/"),
    "prometheus_intro": ("Prometheus Docs: Introduction", "https://prometheus.io/docs/introduction/overview/"),
    "grafana_docs": ("Grafana Docs", "https://grafana.com/docs/grafana/latest/"),
    "testing_library": (
        "Testing Library: React Testing Library Intro",
        "https://testing-library.com/docs/react-testing-library/intro/",
    ),
    "playwright_intro": ("Playwright Docs: Introduction", "https://playwright.dev/docs/intro"),
    "jest_getting_started": ("Jest Docs: Getting Started", "https://jestjs.io/docs/getting-started"),
    "github_actions": (
        "GitHub Actions: Understanding GitHub Actions",
        "https://docs.github.com/en/actions/about-github-actions/understanding-github-actions",
    ),
    "web_perf": ("web.dev: Learn Performance", "https://web.dev/learn/performance"),
    "wcag": ("W3C: WCAG Overview", "https://www.w3.org/WAI/standards-guidelines/wcag/"),
    "twelve_factor": ("The Twelve-Factor App", "https://12factor.net/"),
    "sre_workbook": ("Google SRE Workbook", "https://sre.google/workbook/table-of-contents/"),
}


def link(key: str) -> dict[str, str]:
    title, url = LINKS[key]
    return {"title": title, "url": url}


CHAPTERS: list[dict[str, Any]] = [
    {
        "id": "01",
        "title": "Platform Bootstrap",
        "feature_explainer": "Create the project skeleton and shared developer workflow for a new ad bidding platform.",
        "business_value": "Fast, repeatable setup prevents execution drag as the team grows.",
        "advancement": [
            "Level 1: Local API + UI boot with health checks.",
            "Level 2: One-command startup/shutdown scripts and env templates.",
            "Level 3: Team-ready onboarding guide with troubleshooting matrix.",
        ],
        "learn": [
            "Identify the minimum services required for a bidding MVP.",
            "Define boundaries between API, jobs, and frontend app.",
            "Set baseline coding and testing standards.",
        ],
        "write": [
            "Initialize Rails API and React app repositories for the training build.",
            "Configure Postgres/Redis and create scripts for fast local boot.",
            "Publish docs/chapter-01.md with architecture and setup proof.",
        ],
        "reading_links": [link("rails_getting_started"), link("rails_api_mode"), link("docker_compose")],
        "review": [
            "Can a new engineer run the project in under 20 minutes?",
            "Are service health checks deterministic and easy to debug?",
            "Is scope constrained enough for feature-by-feature delivery?",
        ],
    },
    {
        "id": "02",
        "title": "Authentication and Tenant Isolation",
        "feature_explainer": "Implement login and strict account scoping so customer data never crosses tenant boundaries.",
        "business_value": "Multi-tenant isolation is mandatory for trust, compliance, and enterprise readiness.",
        "advancement": [
            "Level 1: JWT login/logout and protected routes.",
            "Level 2: Tenant-scoped authorization checks for all domain actions.",
            "Level 3: Security regression tests for cross-tenant attack paths.",
        ],
        "learn": [
            "Differentiate authentication from authorization.",
            "Define tenant resolution rules for every request.",
            "Model account-role permissions for operators and admins.",
        ],
        "write": [
            "Add JWT-based auth endpoints and middleware.",
            "Implement account and membership models with authorization policies.",
            "Add request specs proving cross-tenant access is denied.",
        ],
        "reading_links": [link("rails_security"), link("jwt_intro"), link("owasp_top10")],
        "review": [
            "Do protected endpoints fail safely when auth context is missing?",
            "Can an authenticated user access data from another tenant?",
            "Are auth failures observable in logs without leaking sensitive data?",
        ],
    },
    {
        "id": "03",
        "title": "Campaign Management Core",
        "feature_explainer": "Build the core campaign entity with lifecycle states, validation, and API contracts.",
        "business_value": "Campaign controls are the center of spend planning and operator decision-making.",
        "advancement": [
            "Level 1: CRUD with hard validations.",
            "Level 2: Lifecycle transitions and guard clauses.",
            "Level 3: Contract-stable API responses consumed by frontend forms.",
        ],
        "learn": [
            "Model campaign state transitions and invalid transitions.",
            "Define budget and date constraints at domain level.",
            "Design serializer output for list and detail views.",
        ],
        "write": [
            "Implement campaign create/list/update APIs.",
            "Add validation rules for budgets, dates, and status transitions.",
            "Add request tests for success and failure paths.",
        ],
        "reading_links": [link("rails_models"), link("rails_validations"), link("rails_controller")],
        "review": [
            "Are invalid transitions fully blocked and well messaged?",
            "Do API responses remain stable as fields evolve?",
            "Can operators recover quickly from validation errors?",
        ],
    },
    {
        "id": "04",
        "title": "Budget Pacing Guardrails",
        "feature_explainer": "Add budget pacing logic so spend is distributed safely instead of burning too early.",
        "business_value": "Runaway spend destroys unit economics and stakeholder confidence.",
        "advancement": [
            "Level 1: Daily limit checks.",
            "Level 2: Time-window pacing decisions.",
            "Level 3: Simulation tests for edge traffic spikes.",
        ],
        "learn": [
            "Understand pacing models and failure modes.",
            "Choose where to enforce budget checks in request flow.",
            "Define guardrails for emergency spend cutoff.",
        ],
        "write": [
            "Implement budget consumption checks during bid-serving actions.",
            "Add pacing service with deterministic output for test fixtures.",
            "Record pacing decision reasons for auditability.",
        ],
        "reading_links": [link("postgres_isolation"), link("rails_querying"), link("postgres_explain")],
        "review": [
            "Does pacing prevent budget exhaustion under burst traffic?",
            "Are budget decisions explainable from logs and evidence?",
            "Is fallback behavior clear if pacing service fails?",
        ],
    },
    {
        "id": "05",
        "title": "Ad Group Targeting",
        "feature_explainer": "Introduce ad groups with targeting dimensions (territory, filters, source constraints).",
        "business_value": "Granular targeting enables better ROI and controlled experimentation.",
        "advancement": [
            "Level 1: Ad group CRUD under campaigns.",
            "Level 2: Targeting rule composition and validation.",
            "Level 3: Clone-and-edit workflow for rapid A/B variants.",
        ],
        "learn": [
            "Design ad group boundaries relative to campaign defaults.",
            "Model targeting settings without over-coupling.",
            "Define safe duplication behavior for experimentation.",
        ],
        "write": [
            "Add ad group APIs with campaign-scoped permissions.",
            "Implement targeting rule model and validation.",
            "Add duplicate endpoint that safely copies configurations.",
        ],
        "reading_links": [link("rails_associations"), link("rails_routing"), link("rails_migrations")],
        "review": [
            "Can targeting be changed without touching campaign-level invariants?",
            "Does clone logic avoid stale IDs and hidden coupling?",
            "Are operators protected from invalid targeting combinations?",
        ],
    },
    {
        "id": "06",
        "title": "Creative Asset Pipeline",
        "feature_explainer": "Build creative management so ad assets can be created, updated, and attached safely.",
        "business_value": "Faster creative iteration directly affects CTR and campaign performance.",
        "advancement": [
            "Level 1: Creative CRUD and attachment.",
            "Level 2: Validation and media constraints.",
            "Level 3: Change history and rollback-safe updates.",
        ],
        "learn": [
            "Define creative ownership and reusability policy.",
            "Set validation boundaries for titles, URLs, and media.",
            "Plan attachment rules between creatives and ad groups.",
        ],
        "write": [
            "Implement creative create/edit/delete endpoints.",
            "Link creatives to ad groups with permission checks.",
            "Track last-modified metadata for audit and debugging.",
        ],
        "reading_links": [link("rails_active_storage"), link("rails_validations"), link("owasp_input_validation")],
        "review": [
            "Can operators swap creatives without data corruption?",
            "Are broken/invalid media assets blocked early?",
            "Is creative change history enough for incident RCA?",
        ],
    },
    {
        "id": "07",
        "title": "Bid Strategy Engine",
        "feature_explainer": "Add bid suggestion and apply flow driven by target CPA and delivery signals.",
        "business_value": "Bid quality determines acquisition cost and margin stability.",
        "advancement": [
            "Level 1: Static bid suggestions by simple rules.",
            "Level 2: Dynamic suggestions using campaign performance inputs.",
            "Level 3: Safety rails with max/min clamps and explanation metadata.",
        ],
        "learn": [
            "Understand CPA and conversion-rate tradeoffs in bidding.",
            "Design deterministic recommendation logic for testability.",
            "Model bid history as auditable events.",
        ],
        "write": [
            "Implement a recommendation service and preview endpoint.",
            "Build bid-apply endpoint with bounds checks and reason codes.",
            "Store bid-change history with operator and timestamp.",
        ],
        "reading_links": [link("postgres_indexes"), link("postgres_explain"), link("rails_querying")],
        "review": [
            "Do suggestions improve performance in sample backtests?",
            "Are extreme bid spikes prevented by hard limits?",
            "Can operators understand why each recommendation exists?",
        ],
    },
    {
        "id": "08",
        "title": "Lead Intake and Quality Gate",
        "feature_explainer": "Ingest inbound leads with schema validation, deduping, and abuse protection.",
        "business_value": "Lead quality drives revenue quality and partner trust.",
        "advancement": [
            "Level 1: Validated lead ingestion endpoint.",
            "Level 2: Duplicate detection and rejection codes.",
            "Level 3: Quality scoring hooks for downstream routing.",
        ],
        "learn": [
            "Define minimum valid lead payload.",
            "Choose dedup strategy and lookback windows.",
            "Design error contracts for partners and internal teams.",
        ],
        "write": [
            "Build lead ingestion endpoint with schema checks.",
            "Add duplicate detection and response taxonomy.",
            "Write tests for malformed, duplicate, and valid payloads.",
        ],
        "reading_links": [link("rails_api_mode"), link("rails_controller"), link("owasp_input_validation")],
        "review": [
            "Are invalid payloads rejected with useful diagnostics?",
            "Does dedup logic avoid false positives and false negatives?",
            "Is throughput acceptable during traffic spikes?",
        ],
    },
    {
        "id": "09",
        "title": "Conversion Attribution",
        "feature_explainer": "Track conversion events and map them to campaigns/ad groups reliably.",
        "business_value": "Accurate attribution is required for optimization and billing confidence.",
        "advancement": [
            "Level 1: Conversion event ingestion.",
            "Level 2: Campaign/ad-group matching with confidence flags.",
            "Level 3: Idempotent retries and reconciliation reporting.",
        ],
        "learn": [
            "Define attribution keys and fallback matching behavior.",
            "Understand idempotency requirements under retries.",
            "Plan mismatch handling and correction workflows.",
        ],
        "write": [
            "Create conversion endpoint for pixel/API inputs.",
            "Implement idempotency keys and duplicate-safe writes.",
            "Add attribution mismatch logs for manual investigation.",
        ],
        "reading_links": [link("stripe_idempotency"), link("rails_models"), link("postgres_isolation")],
        "review": [
            "Can repeated conversion events create duplicates?",
            "Are unmatched conversions surfaced and triaged quickly?",
            "Do attribution outputs align with campaign analytics?",
        ],
    },
    {
        "id": "10",
        "title": "Background Jobs and Retry Safety",
        "feature_explainer": "Move heavy/slow tasks to async workers with robust retry and observability.",
        "business_value": "Async processing protects API latency and improves system resilience.",
        "advancement": [
            "Level 1: Queue-backed job execution.",
            "Level 2: Retry strategy and dead-letter handling.",
            "Level 3: Operational dashboard and replay tooling.",
        ],
        "learn": [
            "Identify synchronous bottlenecks that should become jobs.",
            "Design idempotent worker behavior.",
            "Define queue health metrics and SLOs.",
        ],
        "write": [
            "Implement workers for conversion import or enrichment tasks.",
            "Add retry/backoff policy and dead-job handling path.",
            "Expose queue status metrics for operations.",
        ],
        "reading_links": [link("rails_active_job"), link("sidekiq_best_practices"), link("redis_docs")],
        "review": [
            "Do retries stay safe under partial downstream failures?",
            "Can failed jobs be replayed without duplicating business events?",
            "Is queue latency visible and alertable?",
        ],
    },
    {
        "id": "11",
        "title": "Billing Ledger and Receipts",
        "feature_explainer": "Create immutable billing events and receipt records tied to monetizable actions.",
        "business_value": "Financial correctness underpins invoicing, trust, and audits.",
        "advancement": [
            "Level 1: Receipt creation on billable events.",
            "Level 2: Reconciliation views for daily totals.",
            "Level 3: Refund/adjustment entries with full audit trail.",
        ],
        "learn": [
            "Model append-only financial events.",
            "Define invariants for amount, currency, and timestamps.",
            "Understand reconciliation flow between events and invoices.",
        ],
        "write": [
            "Implement receipt model and API endpoints.",
            "Create billing event log tied to lead/conversion events.",
            "Add reconciliation checks for daily account totals.",
        ],
        "reading_links": [link("stripe_billing"), link("postgres_isolation"), link("rails_validations")],
        "review": [
            "Are financial events immutable after write?",
            "Do totals reconcile across API and reports?",
            "Are refund corrections traceable and reversible?",
        ],
    },
    {
        "id": "12",
        "title": "Analytics Aggregation API",
        "feature_explainer": "Build account-scoped analytics endpoints for KPI cards, trends, and breakdown tables.",
        "business_value": "Good analytics enable faster, better bid decisions.",
        "advancement": [
            "Level 1: Basic KPI aggregation endpoints.",
            "Level 2: Filtered analytics by date/source/status.",
            "Level 3: Optimized queries and precompute strategy where needed.",
        ],
        "learn": [
            "Define a stable analytics contract for frontend consumption.",
            "Choose query strategy: live aggregation vs materialized snapshots.",
            "Plan consistency checks between summary and detail numbers.",
        ],
        "write": [
            "Implement analytics service layer and dashboard endpoints.",
            "Add filtering and pagination for heavy result sets.",
            "Profile and optimize the slowest query path.",
        ],
        "reading_links": [link("rails_querying"), link("postgres_mv"), link("postgres_explain")],
        "review": [
            "Do KPI cards reconcile with detailed tables?",
            "Is p95 analytics latency acceptable for operator workflows?",
            "Can analytics failures degrade gracefully?",
        ],
    },
    {
        "id": "13",
        "title": "React Shell and Protected Navigation",
        "feature_explainer": "Create the frontend shell with authenticated routing and role-aware navigation.",
        "business_value": "A stable shell reduces UI regressions and speeds feature rollout.",
        "advancement": [
            "Level 1: Authenticated route gates.",
            "Level 2: Role-aware menus and access control UX.",
            "Level 3: Session-expiry handling and graceful re-auth flows.",
        ],
        "learn": [
            "Design route boundaries for public, operator, and admin areas.",
            "Model global auth state and account context.",
            "Define failure behavior for token expiry and permission errors.",
        ],
        "write": [
            "Build app shell layout and route protection.",
            "Wire login/logout and token persistence.",
            "Render clear unauthorized/session-expired states.",
        ],
        "reading_links": [link("react_learn"), link("react_router"), link("redux_essentials")],
        "review": [
            "Can users deep-link into protected pages safely?",
            "Do role changes reflect correctly without full app reload?",
            "Is navigation behavior consistent across error states?",
        ],
    },
    {
        "id": "14",
        "title": "Campaign Builder UI",
        "feature_explainer": "Implement campaign list/create/edit flows with robust form validation and feedback.",
        "business_value": "Fast, clear campaign setup improves execution speed for growth teams.",
        "advancement": [
            "Level 1: Create and list campaigns.",
            "Level 2: Edit workflow with optimistic updates where safe.",
            "Level 3: Validation UX and reusable form primitives.",
        ],
        "learn": [
            "Design forms for high-risk numeric and schedule fields.",
            "Balance optimistic UI with server-source-of-truth behavior.",
            "Plan data fetching and mutation state handling.",
        ],
        "write": [
            "Build campaign list and create/edit pages.",
            "Integrate with backend validation and error payloads.",
            "Add draft/save patterns for partially complete forms.",
        ],
        "reading_links": [link("react_thinking"), link("react_state"), link("tanstack_query")],
        "review": [
            "Can operators complete common tasks quickly and accurately?",
            "Are validation errors understandable and actionable?",
            "Does stale data handling avoid accidental overwrites?",
        ],
    },
    {
        "id": "15",
        "title": "Ad Group and Bid Console UI",
        "feature_explainer": "Build ad group operations UI with bid recommendation, edit, and history visibility.",
        "business_value": "This is the day-to-day control center for performance operators.",
        "advancement": [
            "Level 1: Ad group list/edit actions.",
            "Level 2: Bid suggestion preview and safe apply.",
            "Level 3: Change history + compare mode for rapid tuning.",
        ],
        "learn": [
            "Design high-speed workflows for repetitive operator actions.",
            "Model mutation safety for risky controls (bid updates).",
            "Define UI evidence for who changed what and when.",
        ],
        "write": [
            "Implement ad group table and edit panels.",
            "Add bid modal with preview and apply actions.",
            "Show bid history and latest change metadata in UI.",
        ],
        "reading_links": [link("react_state"), link("tanstack_query"), link("wcag")],
        "review": [
            "Are risky actions protected by clear confirmation and bounds?",
            "Can operators quickly understand recent bid changes?",
            "Is keyboard navigation workable for heavy users?",
        ],
    },
    {
        "id": "16",
        "title": "Performance Dashboard UI",
        "feature_explainer": "Ship dashboard cards, trends, and tables for spend, leads, conversions, and efficiency.",
        "business_value": "Actionable visibility closes the optimization loop every day.",
        "advancement": [
            "Level 1: KPI cards and summary charts.",
            "Level 2: Filtered tables with drill-down context.",
            "Level 3: Performance budgets and loading-state polish.",
        ],
        "learn": [
            "Select the smallest useful KPI set for bidding decisions.",
            "Design consistent filter state across multiple widgets.",
            "Plan loading, empty, and degraded states.",
        ],
        "write": [
            "Build dashboard page with KPI widgets and trend chart.",
            "Add campaign table with filters and pagination.",
            "Instrument frontend performance and optimize heavy renders.",
        ],
        "reading_links": [link("web_perf"), link("react_state"), link("tanstack_query")],
        "review": [
            "Do table totals and card totals always reconcile?",
            "Does dashboard remain responsive under larger datasets?",
            "Can operators identify next actions from current visuals?",
        ],
    },
    {
        "id": "17",
        "title": "Testing and CI Quality Gates",
        "feature_explainer": "Introduce automated checks across API, UI, and end-to-end critical paths.",
        "business_value": "Reliable release velocity requires predictable quality gates.",
        "advancement": [
            "Level 1: Unit/request/component tests for core behavior.",
            "Level 2: End-to-end happy path + key failure path coverage.",
            "Level 3: CI policy with enforceable pass criteria and artifacts.",
        ],
        "learn": [
            "Design a practical testing pyramid for this product.",
            "Define merge-blocking quality gates.",
            "Plan flaky-test prevention strategy early.",
        ],
        "write": [
            "Add backend request specs and frontend component tests for core flows.",
            "Add one E2E flow covering campaign creation through dashboard visibility.",
            "Configure CI workflow for lint, tests, and build checks.",
        ],
        "reading_links": [link("rails_testing"), link("testing_library"), link("playwright_intro")],
        "review": [
            "Do failing tests clearly explain root cause?",
            "Is CI runtime fast enough for iterative development?",
            "Are critical business flows represented in automated checks?",
        ],
    },
    {
        "id": "18",
        "title": "Launch Hardening and Capstone Defense",
        "feature_explainer": "Run a full launch simulation, incident drill, and final architecture defense.",
        "business_value": "Readiness is proven by operational behavior, not by code volume.",
        "advancement": [
            "Level 1: End-to-end demo of core business flow.",
            "Level 2: Incident response drill with recovery targets.",
            "Level 3: Final defense with tradeoff rationale and prioritized backlog.",
        ],
        "learn": [
            "Define go-live metrics and rollback triggers.",
            "Prepare incident command process and communications.",
            "Summarize architecture tradeoffs for non-engineering stakeholders.",
        ],
        "write": [
            "Execute full demo: auth -> campaign -> bids -> leads -> conversions -> dashboard.",
            "Run one controlled failure simulation and complete recovery runbook.",
            "Publish final capstone report with evidence index and next-phase roadmap.",
        ],
        "reading_links": [link("sre_workbook"), link("opentelemetry"), link("twelve_factor")],
        "review": [
            "Can on-call isolate and mitigate incidents quickly?",
            "Are go-live decisions tied to explicit measurable criteria?",
            "Does the backlog prioritize highest-risk or highest-revenue improvements first?",
        ],
    },
]


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def list_block(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{esc(item)}</li>" for item in items) + "</ul>"


def link_block(items: list[dict[str, str]]) -> str:
    parts = []
    for item in items:
        title = esc(item["title"])
        url = esc(item["url"])
        parts.append(
            f'<li><a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a><span class="url"> ({url})</span></li>'
        )
    return "<ul>" + "".join(parts) + "</ul>"


def chapter_section(chapter: dict[str, Any]) -> str:
    chapter_id = esc(chapter["id"])
    title = esc(chapter["title"])
    feature_explainer = esc(chapter["feature_explainer"])
    business_value = esc(chapter["business_value"])
    return f"""
<section class="page chapter">
  <div class="nav">Table of Contents | Chapter {chapter_id}</div>
  <h2>Chapter {chapter_id}: {title}</h2>

  <p class="feature"><strong>Feature Overview:</strong> {feature_explainer}</p>
  <p class="value"><strong>Why This Feature Matters:</strong> {business_value}</p>

  <h3>Feature Advancement Path</h3>
  {list_block(chapter["advancement"])}

  <div class="step">
    <h3>A. Learn Concept</h3>
    {list_block(chapter["learn"])}
  </div>

  <div class="step">
    <h3>B. Write Code</h3>
    {list_block(chapter["write"])}
  </div>

  <div class="step">
    <h3>C. Suggested Reading (Working Links)</h3>
    {link_block(chapter["reading_links"])}
  </div>

  <div class="step">
    <h3>D. Review</h3>
    {list_block(chapter["review"])}
  </div>

  <p class="evidence"><strong>Evidence to submit:</strong> docs/chapter-{chapter_id}.md, PR link, test output, and review notes.</p>
</section>
"""


def build_html(validated_on: str) -> str:
    toc_rows = "\n".join(
        f"<tr><td>{esc(ch['id'])}</td><td>{esc(ch['title'])}</td><td>Open</td></tr>" for ch in CHAPTERS
    )
    chapter_cards = "\n".join(
        f"""
<article class="card">
  <h4>Chapter {esc(ch["id"])}: {esc(ch["title"])}</h4>
  <p><strong>Feature:</strong> {esc(ch["feature_explainer"])}</p>
  <p><strong>Value:</strong> {esc(ch["business_value"])}</p>
  <p class="format">Format: Learn concept -> Write code -> Suggested reading -> Review</p>
</article>
"""
        for ch in CHAPTERS
    )
    chapter_pages = "\n".join(chapter_section(ch) for ch in CHAPTERS)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ILA Rails React Advanced Curriculum - Feature-by-Feature Ad Bidding Platform</title>
  <style>
    :root {{
      --ink: #0f172a;
      --muted: #334155;
      --line: #cbd5e1;
      --teal-700: #0f766e;
      --bg: #f8fafc;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Helvetica Neue", Arial, sans-serif;
      color: var(--ink);
      line-height: 1.45;
      font-size: 13px;
      background: white;
    }}
    .page {{
      max-width: 860px;
      margin: 0 auto;
      padding: 20px 24px;
    }}
    .cover {{
      background: linear-gradient(180deg, #ecfeff 0%, #ffffff 38%);
      border-bottom: 1px solid var(--line);
    }}
    h1 {{
      margin: 0 0 8px 0;
      color: #115e59;
      font-size: 26px;
    }}
    h2 {{
      margin: 0 0 8px 0;
      font-size: 22px;
    }}
    h3 {{
      margin: 12px 0 6px 0;
      color: var(--teal-700);
      font-size: 15px;
    }}
    h4 {{
      margin: 0 0 5px 0;
      font-size: 14px;
      color: #115e59;
    }}
    p {{ margin: 0 0 8px 0; }}
    ul, ol {{
      margin: 0 0 10px 18px;
      padding: 0;
    }}
    .meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 12px 0;
    }}
    .meta span {{
      border: 1px solid var(--line);
      background: white;
      border-radius: 999px;
      padding: 5px 10px;
      font-size: 12px;
    }}
    .journey {{
      border: 1px solid var(--line);
      background: var(--bg);
      border-radius: 10px;
      padding: 12px;
      margin-top: 10px;
    }}
    .journey li {{ margin-bottom: 5px; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 8px;
    }}
    th, td {{
      border: 1px solid var(--line);
      padding: 7px 8px;
      text-align: left;
      vertical-align: top;
    }}
    th {{ background: #f1f5f9; }}
    .cards {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 8px;
    }}
    .card {{
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 10px 12px;
      background: #ffffff;
    }}
    .format {{
      margin: 0;
      color: #0f766e;
      font-size: 12px;
      font-weight: 600;
    }}
    .chapter {{
      page-break-before: always;
    }}
    .nav {{
      font-size: 11px;
      color: #64748b;
      margin-bottom: 6px;
    }}
    .feature {{
      border: 1px solid var(--line);
      border-left: 4px solid #2563eb;
      background: #eff6ff;
      padding: 8px;
      border-radius: 8px;
    }}
    .value {{
      border: 1px solid var(--line);
      border-left: 4px solid #0f766e;
      background: #f8fafc;
      padding: 8px;
      border-radius: 8px;
      margin-top: 6px;
    }}
    .step {{
      margin-top: 8px;
      padding: 8px 10px;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: #ffffff;
    }}
    .url {{
      color: var(--muted);
      font-size: 11px;
      word-break: break-all;
    }}
    a {{
      color: #0c4a6e;
      text-decoration: underline;
    }}
    .evidence {{
      margin-top: 8px;
      font-size: 12px;
      color: var(--muted);
    }}
    .rubric {{
      page-break-before: always;
    }}
    .validation-note {{
      margin-top: 6px;
      color: #334155;
      font-size: 12px;
    }}
    @media print {{
      a {{
        color: inherit;
      }}
    }}
  </style>
</head>
<body>
  <section class="page cover">
    <h1>ILA (Iksha Learning Academy)</h1>
    <p><strong>Rails and React Advanced Curriculum</strong></p>
    <p>{esc(COURSE["subtitle"])}</p>

    <div class="meta">
      <span>Completion Window: {esc(COURSE["completion_window"])}</span>
      <span>Chapters: {COURSE["chapters"]}</span>
      <span>Track: {esc(COURSE["track"])}</span>
      <span>Certification: {esc(COURSE["certification"])}</span>
    </div>

    <h3>How to Navigate</h3>
    <ol>
      <li>Build one feature per chapter in order. Do not skip chapters.</li>
      <li>Use the Feature Advancement Path to move from basic to advanced implementation.</li>
      <li>Submit chapter evidence in docs/chapter-XX.md with code and test proof.</li>
      <li>Complete D. Review before moving to the next chapter.</li>
    </ol>

    <h3>Chapter Format (Required)</h3>
    <ol>
      <li>Learn concept</li>
      <li>Write code</li>
      <li>Suggested reading (working links)</li>
      <li>Review</li>
    </ol>
    <p class="validation-note">Suggested links validated on: {esc(validated_on)}</p>

    <h3>Learning Journey</h3>
    <ul class="journey">
      <li>{esc(COURSE["journey"][0])}</li>
      <li>{esc(COURSE["journey"][1])}</li>
      <li>{esc(COURSE["journey"][2])}</li>
      <li>{esc(COURSE["journey"][3])}</li>
    </ul>
  </section>

  <section class="page chapter">
    <h2>Table of Contents</h2>
    <table>
      <thead><tr><th>ID</th><th>Feature Chapter</th><th>Page</th></tr></thead>
      <tbody>{toc_rows}</tbody>
    </table>
  </section>

  <section class="page chapter">
    <h2>Chapter Overview Cards</h2>
    <div class="cards">
      {chapter_cards}
    </div>
  </section>

  <section class="page rubric">
    <h2>Evaluation Rubric (Per Chapter)</h2>
    <table>
      <thead><tr><th>Category</th><th>Score</th><th>Expectation</th></tr></thead>
      <tbody>
        <tr><td>Feature Understanding</td><td>/5</td><td>You clearly explain what the feature does and why it matters.</td></tr>
        <tr><td>Implementation Quality</td><td>/5</td><td>Code is robust, tested, and operationally safe.</td></tr>
        <tr><td>Step-by-Step Advancement</td><td>/5</td><td>The feature evolves from basic to advanced with clear milestones.</td></tr>
        <tr><td>Review Rigor</td><td>/5</td><td>You identify bugs, regressions, and scalability risks.</td></tr>
        <tr><td>Evidence Quality</td><td>/5</td><td>Evidence is reproducible and supports all claims.</td></tr>
      </tbody>
    </table>
  </section>

  {chapter_pages}
</body>
</html>
"""


def extract_unique_links(chapters: list[dict[str, Any]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    links: list[dict[str, str]] = []
    for chapter in chapters:
        for item in chapter["reading_links"]:
            url = item["url"]
            if url in seen:
                continue
            seen.add(url)
            links.append(item)
    return links


def check_one_url(url: str, timeout: int = 20) -> tuple[bool, str]:
    last_error = ""
    for method in ("HEAD", "GET"):
        req = Request(url, method=method, headers={"User-Agent": UA})
        try:
            with urlopen(req, timeout=timeout) as resp:
                status = getattr(resp, "status", 200)
                if 200 <= status < 400:
                    return True, f"{status} via {method}"
                last_error = f"{status} via {method}"
        except HTTPError as exc:
            if method == "HEAD" and exc.code in (401, 403, 405, 429):
                last_error = f"{exc.code} via HEAD (retrying GET)"
                continue
            last_error = f"{exc.code} {exc.reason}"
        except (URLError, socket.timeout) as exc:
            last_error = str(exc)
    return False, last_error


def validate_links(chapters: list[dict[str, Any]]) -> None:
    links = extract_unique_links(chapters)
    failures: list[tuple[str, str, str]] = []
    for item in links:
        ok, detail = check_one_url(item["url"])
        if not ok:
            failures.append((item["title"], item["url"], detail))

    if failures:
        lines = ["Link validation failed for the following URLs:"]
        for title, url, detail in failures:
            lines.append(f"- {title}: {url} ({detail})")
        raise RuntimeError("\n".join(lines))


def render_pdf() -> None:
    subprocess.run(
        [
            "wkhtmltopdf",
            "--enable-local-file-access",
            "--margin-top",
            "10",
            "--margin-right",
            "10",
            "--margin-bottom",
            "10",
            "--margin-left",
            "10",
            str(HTML_PATH),
            str(PDF_PATH),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-link-check", action="store_true", help="Skip URL validation before rendering.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.skip_link_check:
        validate_links(CHAPTERS)
    TRACK_DIR.mkdir(parents=True, exist_ok=True)
    validated_on = date.today().isoformat()
    HTML_PATH.write_text(build_html(validated_on=validated_on))
    render_pdf()
    print(f"Generated: {HTML_PATH}")
    print(f"Generated: {PDF_PATH}")
    print(f"Link check: {'skipped' if args.skip_link_check else 'passed'}")


if __name__ == "__main__":
    main()
