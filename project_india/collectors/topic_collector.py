#!/usr/bin/env python3
"""Generic file-based topic collector for Project India.

This collector is intentionally topic-agnostic:

- topic intent lives in `project_india/topics/<topic-slug>/config.yaml`
- raw artifacts are saved under `data/<topic-slug>/raw/`
- no database is required
- no AI summary is generated in this step
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import io
import json
import re
import sys
import urllib.parse
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

import feedparser
import httpx
import yaml
from bs4 import BeautifulSoup

try:
    from readability import Document
except Exception:  # pragma: no cover - optional dependency
    Document = None

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover - optional dependency
    PdfReader = None


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_india.research_taxonomy import DATA_TYPES  # noqa: E402


@dataclass(frozen=True)
class DiscoveredItem:
    title: str | None
    link: str
    published: str | None
    source: str | None


@dataclass(frozen=True)
class StoredDocument:
    sha256: str
    url: str
    title: str | None
    text_path: str
    raw_path: str
    metadata_path: str


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "untitled-topic"


def load_topic_config(config_path: Path) -> dict:
    if not config_path.exists():
        raise FileNotFoundError(f"Topic config not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    if not isinstance(cfg, dict):
        raise ValueError(f"Topic config must be a YAML mapping: {config_path}")
    if not cfg.get("title") and not cfg.get("slug"):
        raise ValueError("Topic config needs at least `title` or `slug`.")
    if not cfg.get("seeds"):
        raise ValueError("Topic config needs a non-empty `seeds` list.")
    return cfg


def resolve_config_path(config: str | None, topic_dir: str | None) -> Path:
    if config:
        return Path(config).expanduser().resolve()
    if topic_dir:
        return (Path(topic_dir).expanduser().resolve() / "config.yaml")
    raise ValueError("Pass either `--config` or `--topic-dir`.")


def topic_slug(cfg: dict) -> str:
    return slugify(str(cfg.get("slug") or cfg.get("title")))


def search_terms(cfg: dict) -> list[str]:
    terms: list[str] = []
    for key in ("keywords", "entities", "queries"):
        value = cfg.get(key) or []
        if isinstance(value, str):
            terms.append(value)
        else:
            terms.extend(str(item) for item in value if item)
    if not terms:
        terms.append(str(cfg.get("slug") or cfg.get("title")))
    return sorted(set(terms), key=str.lower)


def historical_terms(cfg: dict) -> list[str]:
    configured = cfg.get("historical_queries") or cfg.get("queries") or cfg.get("keywords") or []
    if isinstance(configured, str):
        configured = [configured]

    seen: set[str] = set()
    terms: list[str] = []
    for term in configured:
        normalized = str(term).strip()
        key = normalized.lower()
        if normalized and key not in seen:
            terms.append(normalized)
            seen.add(key)

    if not terms:
        terms = [str(cfg.get("title") or cfg.get("slug"))]
    return terms[:6]


def sha256_hex(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def extension_for_response(response: httpx.Response) -> str:
    content_type = (response.headers.get("content-type") or "").lower()
    path = response.url.path.lower()
    if "pdf" in content_type or path.endswith(".pdf"):
        return ".pdf"
    if "json" in content_type or path.endswith(".json"):
        return ".json.raw"
    if "csv" in content_type or path.endswith(".csv"):
        return ".csv"
    if "spreadsheet" in content_type or path.endswith((".xls", ".xlsx")):
        return ".xlsx"
    if "image/" in content_type or path.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".tif", ".tiff")):
        suffix = Path(path).suffix
        return suffix if suffix else ".image"
    if "text/plain" in content_type or path.endswith(".txt"):
        return ".source.txt"
    return ".html"


def classify_data_type(url: str, content_type: str | None, source: str | None) -> str:
    lower_url = url.lower()
    lower_type = (content_type or "").lower()
    lower_source = (source or "").lower()

    if "rss" in lower_source or "feed" in lower_source:
        return "rss_feed_content"
    if "pdf" in lower_type or lower_url.endswith(".pdf"):
        if any(term in lower_url for term in ("court", "judgement", "judgment", "tribunal", "legal")):
            return "legal_judicial_records"
        if any(term in lower_url for term in ("gazette", "notification", "ministry", "gov", "pib")):
            return "government_documents"
        return "pdfs"
    if "json" in lower_type or lower_url.endswith(".json"):
        return "structured_datasets"
    if "csv" in lower_type or lower_url.endswith((".csv", ".xls", ".xlsx")):
        return "structured_datasets"
    if "image/" in lower_type or lower_url.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".tif", ".tiff")):
        return "images"
    if any(domain in lower_url for domain in ("arxiv.org", "crossref.org", "doi.org", "ssrn.com")):
        return "research_papers"
    if any(term in lower_url for term in ("supremecourt", "court", "tribunal", "judgement", "judgment")):
        return "legal_judicial_records"
    if any(term in lower_url for term in ("pib.gov", ".gov", "gazette", "ministry")):
        return "government_documents"
    if any(term in lower_url for term in ("youtube.com", "youtu.be", "vimeo.com")):
        return "video_content"
    if any(term in lower_url for term in ("reddit.com", "forum", "stackexchange", "stackoverflow")):
        return "community_discussions"
    if any(term in lower_url for term in ("webcache", "archive.org", "web.archive.org")):
        return "web_archives_cached_content"
    if any(term in lower_url for term in ("blog", "substack", "medium.com")):
        return "blogs"
    if "html" in lower_type:
        return "websites_html_pages"
    return "news_articles"


def enabled_data_types(topic: dict) -> list[str]:
    configured = topic.get("data_types") or DATA_TYPES
    if isinstance(configured, str):
        configured = [configured]
    return [str(item) for item in configured]


def extract_text(html: str) -> str:
    if Document is not None:
        try:
            article = Document(html).summary()
            text = BeautifulSoup(article, "html.parser").get_text(separator="\n").strip()
            if text:
                return text
        except Exception:
            pass

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    for selector in ("article", "main", "#content", ".article-body", ".main-content"):
        selected = soup.select_one(selector)
        if selected and selected.get_text(strip=True):
            return selected.get_text(separator="\n").strip()

    return soup.get_text(separator="\n").strip()


def extract_pdf_text(content: bytes) -> str:
    if PdfReader is None:
        return ""
    try:
        reader = PdfReader(io.BytesIO(content))
        return "\n".join((page.extract_text() or "").strip() for page in reader.pages).strip()
    except Exception:
        return ""


def extract_response_text(response: httpx.Response) -> str:
    content_type = (response.headers.get("content-type") or "").lower()
    if "pdf" in content_type or response.url.path.lower().endswith(".pdf"):
        text = extract_pdf_text(response.content)
        if text:
            return text
    if "json" in content_type:
        try:
            return json.dumps(response.json(), ensure_ascii=False, indent=2)
        except Exception:
            return response.text
    if "csv" in content_type or response.url.path.lower().endswith(".csv"):
        return response.text
    if "image/" in content_type:
        return ""
    return extract_text(response.text)


async def collect_from_rss(feed_urls: Iterable[str]) -> list[DiscoveredItem]:
    items: list[DiscoveredItem] = []
    for feed_url in feed_urls:
        parsed = feedparser.parse(feed_url)
        for entry in parsed.entries:
            link = entry.get("link") or entry.get("id")
            if not link:
                continue
            items.append(
                DiscoveredItem(
                    title=entry.get("title"),
                    link=link,
                    published=entry.get("published") or entry.get("updated"),
                    source=feed_url,
                )
            )
    return items


def collect_from_urls(urls: Iterable[str], source: str) -> list[DiscoveredItem]:
    return [
        DiscoveredItem(title=None, link=str(url), published=None, source=source)
        for url in urls
        if str(url).strip()
    ]


async def collect_from_gdelt(
    terms: Iterable[str],
    *,
    max_records: int,
    historical_days: int,
    timeout: int,
) -> list[DiscoveredItem]:
    query = " OR ".join(f'"{term}"' for term in terms if term)
    if not query:
        return []

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=historical_days)
    params = {
        "query": query,
        "mode": "ArtList",
        "format": "json",
        "maxrecords": str(max_records),
        "sort": "hybridrel",
        "startdatetime": start.strftime("%Y%m%d%H%M%S"),
        "enddatetime": end.strftime("%Y%m%d%H%M%S"),
    }
    url = "https://api.gdeltproject.org/api/v2/doc/doc?" + urllib.parse.urlencode(params)

    async with httpx.AsyncClient(headers={"User-Agent": "ProjectIndiaCollector/0.1"}) as client:
        payload = await fetch_gdelt_payload(client, url, timeout)
        if payload is None and query.count(" OR ") > 0:
            fallback_params = params | {"query": f'"{next(iter(terms), "")}"', "maxrecords": str(min(max_records, 100))}
            fallback_url = "https://api.gdeltproject.org/api/v2/doc/doc?" + urllib.parse.urlencode(fallback_params)
            payload = await fetch_gdelt_payload(client, fallback_url, timeout)
        if payload is None:
            return []

    items: list[DiscoveredItem] = []
    for article in payload.get("articles", []):
        link = article.get("url")
        if not link:
            continue
        items.append(
            DiscoveredItem(
                title=article.get("title"),
                link=link,
                published=article.get("seendate"),
                source=article.get("sourceCountry") or "gdelt",
            )
        )
    return items


async def fetch_gdelt_payload(client: httpx.AsyncClient, url: str, timeout: int) -> dict | None:
    try:
        response = await client.get(url, timeout=timeout, follow_redirects=True)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        print(f"gdelt discovery error: {exc}")
        return None


def filter_items(items: Iterable[DiscoveredItem], terms: Iterable[str]) -> list[DiscoveredItem]:
    normalized_terms = [term.lower() for term in terms if term]
    filtered: list[DiscoveredItem] = []
    seen: set[str] = set()

    for item in items:
        searchable = " ".join(part for part in (item.title, item.link, item.source) if part).lower()
        if item.link in seen:
            continue
        if any(term in searchable for term in normalized_terms):
            filtered.append(item)
            seen.add(item.link)

    return filtered


def existing_urls(out_dir: Path) -> set[str]:
    urls: set[str] = set()
    for metadata_path in out_dir.glob("*.json"):
        if metadata_path.name.startswith("_run_"):
            continue
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        url = metadata.get("url")
        if url:
            urls.add(str(url))
    return urls


async def fetch_url(client: httpx.AsyncClient, url: str, timeout: int) -> httpx.Response | None:
    try:
        response = await client.get(url, timeout=timeout, follow_redirects=True)
        response.raise_for_status()
        return response
    except Exception as exc:
        print(f"fetch error {url}: {exc}")
        return None


async def fetch_and_store(
    items: list[DiscoveredItem],
    *,
    out_dir: Path,
    topic: dict,
    limit: int,
    concurrency: int,
    timeout: int,
) -> list[StoredDocument]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stored: list[StoredDocument] = []
    semaphore = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(headers={"User-Agent": "ProjectIndiaCollector/0.1"}) as client:

        async def work(item: DiscoveredItem) -> StoredDocument | None:
            async with semaphore:
                response = await fetch_url(client, item.link, timeout)
                if response is None:
                    return None

                content = response.content
                digest = sha256_hex(content)
                raw_path = out_dir / f"{digest}{extension_for_response(response)}"
                text_path = out_dir / f"{digest}.txt"
                metadata_path = out_dir / f"{digest}.json"
                content_type = response.headers.get("content-type")
                data_type = classify_data_type(item.link, content_type, item.source)

                raw_path.write_bytes(content)
                text = extract_response_text(response)
                text_path.write_text(text, encoding="utf-8")

                metadata = {
                    "topic_slug": topic_slug(topic),
                    "topic_title": topic.get("title"),
                    "data_type": data_type,
                    "enabled_data_types": enabled_data_types(topic),
                    "url": item.link,
                    "title": item.title,
                    "source": item.source,
                    "published": item.published,
                    "sha256": digest,
                    "content_type": content_type,
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                    "text_chars": len(text),
                    "raw_path": display_path(raw_path),
                    "text_path": display_path(text_path),
                }
                metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"saved {item.link} -> {digest}")

                return StoredDocument(
                    sha256=digest,
                    url=item.link,
                    title=item.title,
                    text_path=display_path(text_path),
                    raw_path=display_path(raw_path),
                    metadata_path=display_path(metadata_path),
                )

        results = await asyncio.gather(*(work(item) for item in items[:limit]))

    for result in results:
        if result is not None:
            stored.append(result)
    return stored


async def collect_topic(
    *,
    config_path: Path,
    limit: int,
    output_root: Path,
    concurrency: int,
    timeout: int,
    include_historical: bool,
    historical_days: int,
    historical_max_records: int,
) -> list[StoredDocument]:
    cfg = load_topic_config(config_path)
    slug = topic_slug(cfg)
    terms = search_terms(cfg)
    gdelt_terms = historical_terms(cfg)
    seeds = [str(seed) for seed in cfg.get("seeds", [])]
    manual_urls = [str(url) for url in cfg.get("urls", [])]
    out_dir = output_root / slug / "raw"

    print(f"topic: {cfg.get('title') or slug} ({slug})")
    print(f"feeds: {len(seeds)}")
    discovered = await collect_from_rss(seeds)
    print(f"discovered rss: {len(discovered)} items")
    manual_items: list[DiscoveredItem] = []
    if manual_urls:
        manual_items = collect_from_urls(manual_urls, "topic-config")
        print(f"configured urls: {len(manual_items)} items")
    historical_items: list[DiscoveredItem] = []
    if include_historical:
        historical_items = await collect_from_gdelt(
            gdelt_terms,
            max_records=historical_max_records,
            historical_days=historical_days,
            timeout=timeout,
        )
        print(f"discovered historical: {len(historical_items)} items")
    discovered = discovered + historical_items
    matched = filter_items(discovered, terms) + manual_items
    known_urls = existing_urls(out_dir)
    if known_urls:
        before_existing_filter = len(matched)
        matched = [item for item in matched if item.link not in known_urls]
        print(f"already stored: {before_existing_filter - len(matched)} items")
    print(f"matched unique: {len(matched)} items")

    run_metadata = {
        "topic_slug": slug,
        "topic_title": cfg.get("title"),
        "config_path": display_path(config_path),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "feeds": len(seeds),
        "configured_urls": len(manual_urls),
        "historical_enabled": include_historical,
        "historical_days": historical_days if include_historical else None,
        "historical_max_records": historical_max_records if include_historical else None,
        "discovered_items": len(discovered),
        "matched_items": len(matched),
        "limit": limit,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    run_path = out_dir / f"_run_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    run_path.write_text(json.dumps(run_metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    if not matched:
        print("no matching RSS items found")
        return []

    stored = await fetch_and_store(
        matched,
        out_dir=out_dir,
        topic=cfg,
        limit=limit,
        concurrency=concurrency,
        timeout=timeout,
    )
    print(f"stored: {len(stored)} documents in {display_path(out_dir)}")
    return stored


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect raw evidence files for any Project India topic.")
    parser.add_argument("--config", help="Path to a topic config.yaml file.")
    parser.add_argument("--topic-dir", help="Path to a topic folder containing config.yaml.")
    parser.add_argument("--limit", type=int, default=20, help="Maximum matching documents to fetch.")
    parser.add_argument("--output-root", default=str(ROOT / "data"), help="Root folder for collected files.")
    parser.add_argument("--concurrency", type=int, default=6, help="Maximum concurrent page fetches.")
    parser.add_argument("--timeout", type=int, default=15, help="HTTP timeout in seconds.")
    parser.add_argument("--historical", action="store_true", help="Also discover historical URLs from GDELT.")
    parser.add_argument("--historical-days", type=int, default=365, help="Historical lookback window for GDELT.")
    parser.add_argument("--historical-max-records", type=int, default=100, help="Maximum GDELT URLs to discover.")
    args = parser.parse_args()

    config_path = resolve_config_path(args.config, args.topic_dir)
    output_root = Path(args.output_root).expanduser().resolve()
    asyncio.run(
        collect_topic(
            config_path=config_path,
            limit=args.limit,
            output_root=output_root,
            concurrency=args.concurrency,
            timeout=args.timeout,
            include_historical=args.historical,
            historical_days=args.historical_days,
            historical_max_records=args.historical_max_records,
        )
    )


if __name__ == "__main__":
    main()
