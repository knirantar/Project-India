"""Shared research taxonomy for Project India workflows."""
from __future__ import annotations


DATA_TYPES = [
    "news_articles",
    "government_documents",
    "research_papers",
    "books",
    "pdfs",
    "rss_feed_content",
    "structured_datasets",
    "websites_html_pages",
    "blogs",
    "social_media_content",
    "video_content",
    "video_transcripts",
    "audio_content",
    "images",
    "ocr_text",
    "legal_judicial_records",
    "financial_data",
    "scientific_technical_data",
    "geospatial_mapping_data",
    "event_data",
    "timeline_data",
    "entity_data",
    "relationship_data",
    "metrics_numerical_data",
    "metadata",
    "community_discussions",
    "archived_historical_content",
    "open_source_intelligence",
    "web_archives_cached_content",
    "ai_generated_summaries_derived_intelligence",
]


NORMALIZED_OBJECTS = [
    "documents",
    "claims",
    "entities",
    "events",
    "metrics",
    "relationships",
    "timelines",
    "citations",
    "evidence_snippets",
    "source_credibility",
    "tags_topics",
    "geolocation",
    "timestamps",
]


DEFAULT_SOURCE_PRIORITIES = [
    "official",
    "government",
    "legal",
    "research",
    "dataset",
    "financial",
    "technical",
    "news",
    "community",
    "archive",
]
