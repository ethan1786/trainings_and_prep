#!/usr/bin/env python3
"""
Remote Job Finder — scans company career pages for remote-friendly roles.

Supports:
  - Greenhouse ATS (Anthropic, Stripe, Coinbase, Airbnb, Netflix, etc.)
  - Ashby ATS (OpenAI, Snowflake, Cursor, Perplexity, etc.)
  - Workday ATS (Nvidia)
  - Uber custom API

Usage:
  # Default: scan ALL target companies for remote/Boston + staff/principal engineer roles
  python find_remote_jobs.py

  # Check if shortlisted jobs are still live (and find replacements if not)
  python find_remote_jobs.py --check

  # Single company
  python find_remote_jobs.py coinbase
  python find_remote_jobs.py stripe --keyword "staff"

  # Show all jobs (skip remote/location filter)
  python find_remote_jobs.py datadog --all --keyword "staff"

  # Custom company (specify ATS)
  python find_remote_jobs.py mycompany --ats greenhouse
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime
from typing import Optional


# ── Configuration ───────────────────────────────────────────────────────────

# Target companies for the default scan-all mode
# Already applied: airbnb, coinbase, datadog, figma, netflix, stripe
# Manual check (no API): apple, microsoft, linkedin, salesforce, bytedance/tiktok, spotify
# No remote roles: snap, palantir, plaid
TARGET_COMPANIES = [
    "anthropic",
    "block",
    "confluent",
    "databricks",
    "doordash",
    "elastic",
    "lyft",
    "notion",
    "reddit",
    "robinhood",
    "scale",
    "snowflake",
    "uber",
]

# Default filters for scan-all mode
DEFAULT_LOCATION_KEYWORDS = ["remote", "boston"]
DEFAULT_TITLE_KEYWORDS = [
    "staff", "principal", "software engineer", "senior engineer",
    "lead engineer", "senior backend", "senior platform",
]

# Known company → ATS board mappings
# ats: "greenhouse", "ashby", "workday", or "uber"
COMPANY_BOARDS = {
    # Greenhouse
    "airbnb":     {"ats": "greenhouse", "board": "airbnb"},
    "anthropic":  {"ats": "greenhouse", "board": "anthropic"},
    "block":      {"ats": "greenhouse", "board": "block"},
    "coinbase":   {"ats": "greenhouse", "board": "coinbase"},
    "confluent":  {"ats": "ashby", "board": "confluent"},
    "datadog":    {"ats": "greenhouse", "board": "datadog"},
    "databricks": {"ats": "greenhouse", "board": "databricks"},
    "discord":    {"ats": "greenhouse", "board": "discord"},
    "doordash":   {"ats": "greenhouse", "board": "doordashusa"},
    "elastic":    {"ats": "greenhouse", "board": "elastic"},
    "figma":      {"ats": "greenhouse", "board": "figma"},
    "lyft":       {"ats": "greenhouse", "board": "lyft"},
    "notion":     {"ats": "ashby", "board": "notion"},
    "palantir":   {"ats": "greenhouse", "board": "palantir"},
    "plaid":      {"ats": "greenhouse", "board": "plaid"},
    "ramp":       {"ats": "greenhouse", "board": "ramp"},
    "reddit":     {"ats": "greenhouse", "board": "reddit"},
    "replit":     {"ats": "greenhouse", "board": "replit"},
    "robinhood":  {"ats": "greenhouse", "board": "robinhood"},
    "scale":      {"ats": "greenhouse", "board": "scaleai"},
    "snap":       {"ats": "greenhouse", "board": "snap"},
    "spotify":    {"ats": "greenhouse", "board": "spotify"},
    "stripe":     {"ats": "greenhouse", "board": "stripe"},
    "vercel":     {"ats": "greenhouse", "board": "vercel"},
    # Ashby
    "cursor":     {"ats": "ashby", "board": "anysphere"},
    "openai":     {"ats": "ashby", "board": "openai"},
    "perplexity": {"ats": "ashby", "board": "perplexityai"},
    "snowflake":  {"ats": "ashby", "board": "snowflake"},
    # Workday
    "netflix":    {"ats": "workday", "board": "netflix"},
    "nvidia":     {"ats": "workday", "board": "nvidia"},
    # Custom
    "uber":       {"ats": "uber", "board": "uber"},
}

# Workday instance configs: company → (subdomain, site_path)
WORKDAY_CONFIGS = {
    "nvidia":  ("nvidia.wd5.myworkdayjobs.com", "nvidia/NVIDIAExternalCareerSite"),
    "netflix": ("netflix.wd1.myworkdayjobs.com", "netflix/Netflix"),
}


# ── Shortlisted Jobs to Track ────────────────────────────────────────────────
# These are the specific job postings we're monitoring.
# Each entry: company, title, job_id, url, ats, board, priority
SHORTLIST = [
    {
        "company": "stripe",
        "title": "Staff Engineer, Workflow Engine",
        "job_id": "7600571",
        "url": "https://job-boards.greenhouse.io/stripe/jobs/7600571",
        "ats": "greenhouse",
        "board": "stripe",
        "priority": 1,
    },
    {
        "company": "netflix",
        "title": "Software Engineer (L6) - Technical Catalog",
        "job_id": "JR37313",
        "url": "https://netflix.wd1.myworkdayjobs.com/en-US/Netflix/job/USA---Remote/Software-Engineer--L6----Technical-Catalog_JR37313",
        "ats": "workday",
        "board": "netflix",
        "priority": 2,
    },
    {
        "company": "datadog",
        "title": "Staff Software Engineer",
        "job_id": "3210217",
        "url": "https://careers.datadoghq.com/detail/3210217/?gh_jid=3210217",
        "ats": "greenhouse",
        "board": "datadog",
        "priority": 3,
    },
    {
        "company": "coinbase",
        "title": "Senior Staff Software Engineer - Financial Hub",
        "job_id": "7587071",
        "url": "https://job-boards.greenhouse.io/coinbase/jobs/7587071",
        "ats": "greenhouse",
        "board": "coinbase",
        "priority": 4,
    },
    {
        "company": "airbnb",
        "title": "Senior Staff Engineer, Performance",
        "job_id": "7315583",
        "url": "https://job-boards.greenhouse.io/airbnb/jobs/7315583",
        "ats": "greenhouse",
        "board": "airbnb",
        "priority": 5,
    },
    {
        "company": "figma",
        "title": "Software Engineer, Distributed Systems",
        "job_id": "5552549004",
        "url": "https://boards.greenhouse.io/figma/jobs/5552549004?gh_jid=5552549004",
        "ats": "greenhouse",
        "board": "figma",
        "priority": 6,
    },
    {
        "company": "circle",
        "title": "Distinguished Software Engineer",
        "job_id": "JR100849",
        "url": "https://careers.circle.com/us/en/job/JR100849/Distinguished-Software-Engineer",
        "ats": "custom",
        "board": "circle",
        "priority": 7,
    },
    {
        "company": "netflix",
        "title": "Senior Software Engineer (L5) - Games",
        "job_id": "JR38527",
        "url": "https://explore.jobs.netflix.net/careers/job/790313749790",
        "ats": "workday",
        "board": "netflix",
        "priority": 99,  # backup
    },
]


# ── HTTP Helper ─────────────────────────────────────────────────────────────

def _http_json(url: str, method: str = "GET", body: Optional[dict] = None,
               headers: Optional[dict] = None) -> dict:
    """HTTP request returning parsed JSON."""
    hdrs = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    if headers:
        hdrs.update(headers)
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} — {e.reason} ({url})")
    except urllib.error.URLError as e:
        raise RuntimeError(f"URL error — {e.reason} ({url})")


# ── ATS Fetchers ────────────────────────────────────────────────────────────
# Each returns a list of normalized job dicts with keys:
#   title, location, department, team, is_remote, url, compensation, updated_at

def fetch_greenhouse(board_token: str) -> list[dict]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"
    data = _http_json(url)
    results = []
    for j in data.get("jobs", []):
        loc = j.get("location", {}).get("name", "Unknown")
        depts = [d.get("name", "") for d in j.get("departments", [])]
        results.append({
            "title": j.get("title", "Unknown"),
            "location": loc,
            "department": ", ".join(depts) if depts else "N/A",
            "team": "N/A",
            "is_remote": "remote" in loc.lower(),
            "url": f"https://job-boards.greenhouse.io/{board_token}/jobs/{j.get('id','')}",
            "compensation": "",
            "updated_at": j.get("updated_at", ""),
        })
    return results


def fetch_ashby(board_name: str) -> list[dict]:
    url = f"https://api.ashbyhq.com/posting-api/job-board/{board_name}?includeCompensation=true"
    data = _http_json(url)
    results = []
    for j in data.get("jobs", []):
        if not j.get("isListed", True):
            continue
        loc = j.get("location", "Unknown") or "Unknown"
        secondary = j.get("secondaryLocations", [])
        if secondary:
            sec = [s.get("location", "") for s in secondary if s.get("location")]
            if sec:
                loc = loc + "; " + "; ".join(sec)
        comp = j.get("compensation", {})
        comp_str = (comp.get("compensationTierSummary", "") or "") if comp else ""
        results.append({
            "title": j.get("title", "Unknown"),
            "location": loc,
            "department": j.get("department", "N/A") or "N/A",
            "team": j.get("team", "N/A") or "N/A",
            "is_remote": j.get("isRemote", False),
            "url": j.get("jobUrl", ""),
            "compensation": comp_str,
            "updated_at": j.get("publishedAt", ""),
        })
    return results


def fetch_workday(company: str, search_terms: Optional[list[str]] = None) -> list[dict]:
    """Fetch jobs from a Workday instance.

    If search_terms is provided, runs targeted searches (fast, ~1 req per term).
    Otherwise, paginates through ALL jobs (slow for large boards, 20 per page).
    """
    if company not in WORKDAY_CONFIGS:
        raise ValueError(f"No Workday config for '{company}'. Add it to WORKDAY_CONFIGS.")
    host, site_path = WORKDAY_CONFIGS[company]
    base = f"https://{host}/wday/cxs/{site_path}/jobs"
    site_name = site_path.split("/")[-1]

    def _parse_postings(postings: list[dict]) -> list[dict]:
        out = []
        for j in postings:
            loc = j.get("locationsText", "Unknown")
            ext_path = j.get("externalPath", "")
            url = f"https://{host}/en-US/{site_name}{ext_path}" if ext_path else ""
            out.append({
                "title": j.get("title", "Unknown"),
                "location": loc,
                "department": "N/A",
                "team": "N/A",
                "is_remote": "remote" in loc.lower(),
                "url": url,
                "compensation": "",
                "updated_at": j.get("postedOn", ""),
            })
        return out

    if search_terms:
        # Fast mode: run one search per term, deduplicate by URL
        seen_urls = set()
        results = []
        for term in search_terms:
            offset = 0
            while True:
                body = {"appliedFacets": {}, "limit": 20, "offset": offset, "searchText": term}
                data = _http_json(base, method="POST", body=body)
                postings = data.get("jobPostings", [])
                if not postings:
                    break
                total = data.get("total", 0) if offset == 0 else total
                for parsed in _parse_postings(postings):
                    if parsed["url"] not in seen_urls:
                        seen_urls.add(parsed["url"])
                        results.append(parsed)
                offset += 20
                if offset >= total:
                    break
        return results
    else:
        # Full mode: paginate everything
        results = []
        offset = 0
        total = None
        while True:
            body = {"appliedFacets": {}, "limit": 20, "offset": offset, "searchText": ""}
            data = _http_json(base, method="POST", body=body)
            if total is None:
                total = data.get("total", 0)
                print(f"  Workday reports {total} total jobs (paginating 20 at a time) ...")
            postings = data.get("jobPostings", [])
            if not postings:
                break
            results.extend(_parse_postings(postings))
            offset += 20
            if offset >= total:
                break
        return results


def fetch_uber() -> list[dict]:
    """Fetch jobs from Uber's custom career API."""
    url = "https://www.uber.com/api/loadSearchJobsResults?localeCode=en"
    body = {"params": {"location": [], "department": [], "team": []}}
    headers = {"x-csrf-token": "x"}
    data = _http_json(url, method="POST", body=body, headers=headers)
    results = []
    for j in data.get("data", {}).get("results", []):
        loc_obj = j.get("location", {})
        city = loc_obj.get("city", "")
        region = loc_obj.get("region", "")
        country = loc_obj.get("countryName", "")
        loc_parts = [p for p in [city, region, country] if p]
        loc = ", ".join(loc_parts) if loc_parts else "Unknown"
        # Check all locations
        all_locs = j.get("allLocations", [])
        all_loc_strs = []
        for al in all_locs:
            parts = [al.get("city", ""), al.get("region", "")]
            all_loc_strs.append(", ".join(p for p in parts if p))
        if len(all_loc_strs) > 1:
            loc = " | ".join(all_loc_strs)
        # Detect remote from location fields only (description has too many false positives)
        all_loc_text = loc.lower()
        is_remote = "remote" in all_loc_text
        # Level mapping for display
        level = str(j.get("level", ""))
        level_label = {"5B": "Staff", "6": "Sr Staff", "7": "Principal", "8": "Distinguished"}.get(level, f"L{level}")
        job_id = j.get("id", "")
        results.append({
            "title": j.get("title", "Unknown"),
            "location": loc,
            "department": j.get("department", "N/A") or "N/A",
            "team": j.get("team", "N/A") or "N/A",
            "is_remote": is_remote,
            "url": f"https://www.uber.com/careers/list/{job_id}/" if job_id else "",
            "compensation": "",
            "updated_at": j.get("updatedDate", ""),
            "_level": level,
            "_level_label": level_label,
        })
    return results


def fetch_jobs(company: str, workday_search_terms: Optional[list[str]] = None) -> list[dict]:
    """Fetch jobs for a known company. Returns normalized job list.

    For Workday companies, pass workday_search_terms to use fast targeted search
    instead of slow full pagination.
    """
    if company not in COMPANY_BOARDS:
        raise ValueError(f'Unknown company "{company}". Known: {", ".join(sorted(COMPANY_BOARDS.keys()))}')
    info = COMPANY_BOARDS[company]
    ats = info["ats"]
    board = info["board"]
    if ats == "greenhouse":
        return fetch_greenhouse(board)
    elif ats == "ashby":
        return fetch_ashby(board)
    elif ats == "workday":
        return fetch_workday(company, search_terms=workday_search_terms)
    elif ats == "uber":
        return fetch_uber()
    else:
        raise ValueError(f"Unknown ATS type: {ats}")


# ── Shortlist Checking ──────────────────────────────────────────────────────

def _http_head(url: str) -> int:
    """Return HTTP status code for a URL (follows redirects). Returns 0 on error."""
    hdrs = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    req = urllib.request.Request(url, headers=hdrs, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def _check_greenhouse_job(board: str, job_id: str) -> bool:
    """Check if a specific Greenhouse job is still listed."""
    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs/{job_id}"
    try:
        _http_json(url)
        return True
    except Exception:
        return False


def _check_workday_job(company: str, job_id: str) -> bool:
    """Check if a Workday job is still findable by searching its ID."""
    if company not in WORKDAY_CONFIGS:
        return False
    host, site_path = WORKDAY_CONFIGS[company]
    base = f"https://{host}/wday/cxs/{site_path}/jobs"
    try:
        data = _http_json(base, method="POST", body={
            "appliedFacets": {}, "limit": 5, "offset": 0, "searchText": job_id,
        })
        for posting in data.get("jobPostings", []):
            if job_id in posting.get("bulletFields", []) or job_id in posting.get("title", "") or job_id in posting.get("externalPath", ""):
                return True
            ext = posting.get("externalPath", "")
            if job_id.replace("-", "") in ext.replace("-", ""):
                return True
        return data.get("total", 0) > 0
    except Exception:
        return False


def _find_similar_jobs(company: str, title_hint: str, location_keywords: list[str]) -> list[dict]:
    """Find similar jobs at a company that match location and title hint."""
    try:
        ats_type = COMPANY_BOARDS.get(company, {}).get("ats", "")
        if ats_type == "workday":
            jobs = fetch_jobs(company, workday_search_terms=[title_hint])
        else:
            jobs = fetch_jobs(company)
    except Exception:
        return []
    # Filter by location
    loc_filtered = [j for j in jobs if matches_location(j, location_keywords)]
    # Filter by title hint keywords
    hint_words = [w.lower() for w in title_hint.split() if len(w) > 3]
    scored = []
    for j in loc_filtered:
        t = j["title"].lower()
        score = sum(1 for w in hint_words if w in t)
        if score > 0:
            scored.append((score, j))
    scored.sort(key=lambda x: -x[0])
    return [j for _, j in scored[:5]]


def check_shortlist(output_dir: str):
    """Check if all shortlisted jobs are still live, suggest replacements for dead ones."""
    print()
    print("=" * 90)
    print("CHECKING SHORTLISTED JOB POSTINGS")
    print(f"Tracked jobs: {len(SHORTLIST)}")
    print("=" * 90)

    alive = []
    dead = []

    for entry in sorted(SHORTLIST, key=lambda x: x["priority"]):
        company = entry["company"]
        title = entry["title"]
        ats = entry["ats"]
        job_id = entry.get("job_id")
        url = entry.get("url")
        pri = entry["priority"]
        pri_label = "backup" if pri >= 99 else f"#{pri}"

        print(f"\n  [{pri_label}] {company.upper()} — {title}")

        if ats == "custom" or not job_id:
            # For custom ATS (Circle) or unknown IDs, do a HEAD check on URL
            if url:
                status = _http_head(url)
                # Circle returns 200 even for filled jobs, so we can't reliably check
                print(f"      URL responds {status} — verify manually: {url}")
                alive.append(entry)
            else:
                print(f"      No URL/ID — search via API ...")
                search_hint = entry.get("search_title", title)
                similar = _find_similar_jobs(company, search_hint, DEFAULT_LOCATION_KEYWORDS)
                if similar:
                    print(f"      Found {len(similar)} similar role(s):")
                    for s in similar:
                        print(f"        • {s['title']} — {s['location']}")
                        print(f"          {s['url']}")
                    alive.append(entry)
                else:
                    print(f"      ⚠ No matching roles found")
                    dead.append(entry)
        elif ats == "greenhouse":
            board = entry["board"]
            is_live = _check_greenhouse_job(board, job_id)
            if is_live:
                print(f"      ✅ Still live")
                alive.append(entry)
            else:
                print(f"      ❌ Not found on board — may be closed")
                dead.append(entry)
        elif ats == "workday":
            is_live = _check_workday_job(company, job_id)
            if is_live:
                print(f"      ✅ Still live")
                alive.append(entry)
            else:
                print(f"      ❌ Not found — may be closed")
                dead.append(entry)
        else:
            print(f"      ⚠ Unknown ATS '{ats}' — verify manually: {url}")
            alive.append(entry)

    # Summary
    print(f"\n{'=' * 90}")
    print(f"SUMMARY: {len(alive)} alive, {len(dead)} possibly closed")
    print(f"{'=' * 90}")

    if dead:
        print(f"\n⚠ The following jobs may be closed — searching for replacements:\n")
        for entry in dead:
            company = entry["company"]
            title = entry["title"]
            print(f"  {company.upper()} — {title}")
            search_hint = entry.get("search_title", title.split(",")[0].split("-")[0].strip())
            similar = _find_similar_jobs(company, search_hint, DEFAULT_LOCATION_KEYWORDS)
            if similar:
                print(f"    Possible replacements:")
                for s in similar:
                    print(f"      • {s['title']} — {s['location']}")
                    print(f"        {s['url']}")
            else:
                print(f"    No similar roles found on {company}'s board.")
            print()

    # Save report
    out_path = os.path.join(output_dir, "job_shortlist_check.txt")
    with open(out_path, "w") as f:
        f.write(f"Job Shortlist Status Check\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"{'=' * 70}\n\n")
        for entry in sorted(SHORTLIST, key=lambda x: x["priority"]):
            pri = entry["priority"]
            pri_label = "backup" if pri >= 99 else f"#{pri}"
            status = "ALIVE" if entry in alive else "CLOSED?"
            f.write(f"[{pri_label}] {entry['company'].upper()} — {entry['title']}\n")
            f.write(f"  Status: {status}\n")
            if entry.get("url"):
                f.write(f"  URL: {entry['url']}\n")
            f.write("\n")
    print(f"\nReport saved to: {out_path}")
    print()


# ── Filtering ───────────────────────────────────────────────────────────────

def matches_any_keyword(text: str, keywords: list[str]) -> bool:
    """Check if text contains any of the keywords (case-insensitive)."""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


def matches_location(job: dict, location_keywords: list[str]) -> bool:
    """Check if job location matches any of the location keywords or isRemote."""
    if job.get("is_remote"):
        return True
    loc = job.get("location", "").lower()
    return any(kw.lower() in loc for kw in location_keywords)


# ── Display ─────────────────────────────────────────────────────────────────

def format_job_line(i: int, job: dict, show_level: bool = False) -> str:
    """Format a single job for display."""
    lines = [f"  {i}. {job['title']}"]
    lines.append(f"     Location:   {job['location']}")
    lines.append(f"     Department: {job['department']}")
    if job["team"] != "N/A":
        lines.append(f"     Team:       {job['team']}")
    if show_level and job.get("_level_label"):
        lines.append(f"     Level:      {job['_level_label']} ({job.get('_level','')})")
    if job["compensation"]:
        lines.append(f"     Comp:       {job['compensation']}")
    lines.append(f"     URL:        {job['url']}")
    return "\n".join(lines)


def print_and_save(jobs: list[dict], header: str, output_path: str,
                   show_level: bool = False):
    """Print results to stdout and save to file."""
    print()
    print("=" * 90)
    print(header)
    print("=" * 90)

    if not jobs:
        print("\nNo matching jobs found.\n")
        with open(output_path, "w") as f:
            f.write(f"{header}\nNo matching jobs found.\n")
        return

    print(f"\nFound {len(jobs)} matching job(s):\n")
    lines_out = []
    for i, job in enumerate(jobs, 1):
        block = format_job_line(i, job, show_level=show_level)
        print(block)
        print()
        lines_out.append(block)

    with open(output_path, "w") as f:
        f.write(f"{header}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Total: {len(jobs)}\n")
        f.write("=" * 90 + "\n\n")
        f.write("\n\n".join(lines_out))
        f.write("\n")
    print(f"Results saved to: {output_path}")
    print()


# ── Commands ────────────────────────────────────────────────────────────────

def scan_single(company: str, keyword: Optional[str], location_keywords: list[str],
                show_all: bool, output_dir: str):
    """Scan a single company."""
    print(f"\n{'─'*60}")
    print(f"Scanning {company.upper()} ...")
    print(f"{'─'*60}")
    try:
        all_jobs = fetch_jobs(company)
    except Exception as e:
        print(f"  ERROR: {e}")
        return
    print(f"  Total jobs on board: {len(all_jobs)}")

    filtered = all_jobs
    show_level = (company == "uber")

    if not show_all:
        filtered = [j for j in filtered if matches_location(j, location_keywords)]

    if keyword:
        filtered = [j for j in filtered if matches_any_keyword(j["title"], [keyword])]

    filtered.sort(key=lambda x: x["title"])

    mode = "all" if show_all else "remote"
    suffix = f"_{keyword}" if keyword else ""
    out_path = os.path.join(output_dir, f"jobs_{company}_{mode}{suffix}.txt")

    header_parts = []
    if show_all:
        header_parts.append(f"ALL Jobs at {company.upper()}")
    else:
        header_parts.append(f"Remote/Boston Jobs at {company.upper()}")
    if keyword:
        header_parts.append(f'Title filter: "{keyword}"')
    header = " | ".join(header_parts)

    print_and_save(filtered, header, out_path, show_level=show_level)


def scan_all(output_dir: str):
    """Default command: scan all target companies for remote/Boston + staff/principal engineer roles."""
    print()
    print("=" * 90)
    print("SCANNING ALL TARGET COMPANIES")
    print(f"Companies: {', '.join(TARGET_COMPANIES)}")
    print(f"Location filter: {DEFAULT_LOCATION_KEYWORDS}")
    print(f"Title filter: {DEFAULT_TITLE_KEYWORDS}")
    print("=" * 90)

    all_matches = []

    for company in TARGET_COMPANIES:
        print(f"\n{'─'*60}")
        print(f"Scanning {company.upper()} ...")
        print(f"{'─'*60}")
        try:
            # For Workday companies, use targeted search terms for speed
            ats_type = COMPANY_BOARDS.get(company, {}).get("ats", "")
            if ats_type == "workday":
                search_terms = DEFAULT_TITLE_KEYWORDS
                print(f"  (Workday: using targeted search for speed)")
                jobs = fetch_jobs(company, workday_search_terms=search_terms)
            else:
                jobs = fetch_jobs(company)
        except Exception as e:
            print(f"  ERROR: {e}")
            continue
        print(f"  Total jobs fetched: {len(jobs)}")

        # Filter: location must be remote or Boston
        loc_filtered = [j for j in jobs if matches_location(j, DEFAULT_LOCATION_KEYWORDS)]
        # Filter: title must match one of the title keywords
        title_filtered = [j for j in loc_filtered
                          if matches_any_keyword(j["title"], DEFAULT_TITLE_KEYWORDS)]

        print(f"  After location filter: {len(loc_filtered)}")
        print(f"  After title filter:    {len(title_filtered)}")

        for j in title_filtered:
            j["_company"] = company.upper()
        all_matches.extend(title_filtered)

    # Sort by company then title
    all_matches.sort(key=lambda x: (x.get("_company", ""), x["title"]))

    # Print combined results
    print()
    print("=" * 90)
    header = (f"COMBINED RESULTS: Remote/Boston + Staff/Principal/Senior Engineer\n"
              f"Companies: {', '.join(c.upper() for c in TARGET_COMPANIES)}")
    print(header)
    print("=" * 90)

    if not all_matches:
        print("\nNo matching jobs found.\n")
    else:
        print(f"\nFound {len(all_matches)} matching job(s):\n")
        current_company = ""
        idx = 0
        for job in all_matches:
            co = job.get("_company", "")
            if co != current_company:
                current_company = co
                print(f"\n  ── {current_company} ──")
            idx += 1
            show_level = (co.lower() == "uber")
            block = format_job_line(idx, job, show_level=show_level)
            print(block)
            print()

    # Save combined results
    out_path = os.path.join(output_dir, "jobs_all_targets.txt")
    with open(out_path, "w") as f:
        f.write(f"Remote/Boston + Staff/Principal/Senior Engineer Jobs\n")
        f.write(f"Companies: {', '.join(c.upper() for c in TARGET_COMPANIES)}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Location filter: {DEFAULT_LOCATION_KEYWORDS}\n")
        f.write(f"Title filter: {DEFAULT_TITLE_KEYWORDS}\n")
        f.write(f"Total matches: {len(all_matches)}\n")
        f.write("=" * 90 + "\n\n")
        current_company = ""
        idx = 0
        for job in all_matches:
            co = job.get("_company", "")
            if co != current_company:
                current_company = co
                f.write(f"\n── {current_company} ──\n\n")
            idx += 1
            show_level = (co.lower() == "uber")
            f.write(format_job_line(idx, job, show_level=show_level))
            f.write("\n\n")
    print(f"Combined results saved to: {out_path}")
    print()


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    known = sorted(COMPANY_BOARDS.keys())
    parser = argparse.ArgumentParser(
        description="Find remote-friendly jobs at target companies via their public ATS APIs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Default (no args): scan all target companies for remote/Boston\n"
            "                    + staff/principal/senior engineer roles.\n\n"
            f"Known companies: {', '.join(known)}\n"
            "You can also pass a raw board token with --ats.\n\n"
            "Examples:\n"
            "  python find_remote_jobs.py                          # scan all targets\n"
            "  python find_remote_jobs.py anthropic                # remote jobs at Anthropic\n"
            '  python find_remote_jobs.py openai -k "staff"        # remote + "staff" at OpenAI\n'
            "  python find_remote_jobs.py nvidia --all -k platform # all Nvidia platform jobs\n"
        ),
    )
    parser.add_argument(
        "company",
        nargs="?",
        default=None,
        help="Company name. Omit to scan all target companies.",
    )
    parser.add_argument(
        "--keyword", "-k",
        default=None,
        help='Filter job titles by keyword, e.g. "engineer", "staff", "backend".',
    )
    parser.add_argument(
        "--location", "-l",
        action="append",
        default=None,
        help='Location keywords to match (can specify multiple). Default: "remote", "boston".',
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Show ALL jobs (skip location filter).",
    )
    parser.add_argument(
        "--check", "-c",
        action="store_true",
        help="Check if shortlisted jobs are still live and suggest replacements.",
    )
    parser.add_argument(
        "--ats",
        choices=["greenhouse", "ashby"],
        default=None,
        help="Force a specific ATS type (for unknown companies).",
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=".",
        help="Directory to save output files (default: current directory).",
    )
    args = parser.parse_args()

    location_keywords = args.location if args.location else DEFAULT_LOCATION_KEYWORDS

    if args.check:
        check_shortlist(args.output_dir)
    elif args.company is None:
        # Default: scan all target companies
        scan_all(args.output_dir)
    else:
        company = args.company.lower().strip()
        if company not in COMPANY_BOARDS:
            if args.ats:
                # Add as temporary entry
                COMPANY_BOARDS[company] = {"ats": args.ats, "board": company}
                print(f'"{company}" not in known boards — using {args.ats} with board token "{company}".')
            else:
                print(f'"{company}" not in known boards.')
                print(f"Known companies: {', '.join(known)}")
                print("Use --ats greenhouse|ashby to specify the ATS type.")
                sys.exit(1)
        scan_single(company, args.keyword, location_keywords, args.all, args.output_dir)


if __name__ == "__main__":
    main()
