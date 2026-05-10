# Presentation Workflow

This workflow turns research into clear communication.

## Purpose

Presentations should make complex topics understandable without flattening them. They should show the structure of the issue, the evidence, the stakes, and the choices ahead.

## Presentation Types

- 5-slide quick brief
- 10-12 slide strategic deck
- Sector explainer
- Timeline deck
- Data story
- Decision memo

## Default Deck Structure

1. Title and framing question
2. Why this matters now
3. Current state
4. Historical context or timeline
5. Key actors and institutions
6. Data view
7. Strengths and opportunities
8. Bottlenecks and risks
9. Global comparison
10. Scenarios
11. What India should do next
12. Open questions

## Visual Standards

- Prefer charts, timelines, maps, and matrices over decorative slides.
- Use one main idea per slide.
- Put evidence near the claim it supports.
- Keep source names and dates visible in speaker notes or footers.
- Use consistent colors for India, comparator countries, risks, and opportunities.

## Workflow

1. Start from a topic note.
2. Extract the bottom line.
3. Choose the audience.
4. Define the core message.
5. Build a slide outline in `docs/presentations/`.
6. Add data visuals or diagrams.
7. Convert the outline into a deck when the story is ready.
8. Review for clarity, sourcing, and logic.

## GitHub Automation

Use the `Generate Topic Presentation` GitHub Actions workflow when a topic needs a first draft deck from the repository itself.

Manual inputs:

- `title` - topic title
- `slug` - optional file slug
- `category` - one of `sectors`, `geopolitics`, `internal-growth`, or `research-notes`
- `commit_changes` - whether to commit generated outputs back to the repository

The workflow creates missing topic files, generates a draft PPTX in `docs/presentations/`, updates `data/processed/research_index.json`, uploads the deck as a workflow artifact, and optionally commits the changes.

For serious topics, use `research_mode=deep`. This runs `project-india deep-research` first, which uses OpenAI web search to produce a source-backed topic note, source log, brief, and presentation outline. If `OPENAI_API_KEY` is not configured as a repository secret, the workflow should fail instead of producing a hollow deck.
