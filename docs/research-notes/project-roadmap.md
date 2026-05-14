# Project India Roadmap

This roadmap is the working reference for how Project India should grow from a broad mission into a structured research and analysis system.

## Mission

Project India documents, analyzes, and decodes India's geopolitical position and internal growth across sectors, using AI as a research, writing, analysis, and systems-building partner.

The project should help answer:

What are the forces shaping India's rise, constraints, risks, and opportunities across domestic and global systems?

## Scope

Project India should cover both external and internal dimensions of India's development.

External dimensions:

- Geopolitics and foreign policy
- Strategic competition and alliances
- Trade, supply chains, and global markets
- Defense, security, and technology partnerships
- India's role in the Global South

Internal dimensions:

- Economic growth and industrial policy
- Infrastructure and urban development
- Agriculture and food systems
- Energy, climate, and natural resources
- Technology, AI, and digital public infrastructure
- Education, healthcare, and human development
- Governance, law, institutions, and state capacity
- Social change, culture, and demographics

## Sector Taxonomy

Use this as the initial map of the project.

1. Geopolitics and Foreign Policy
2. Economy and Finance
3. Industry and Manufacturing
4. Infrastructure and Logistics
5. Energy and Climate
6. Agriculture and Food Systems
7. Technology, AI, and Digital Infrastructure
8. Defense and National Security
9. Education and Skills
10. Healthcare and Public Health
11. Governance and Institutions
12. Law, Rights, and Regulation
13. Society, Culture, and Demographics
14. States, Cities, and Regional Development
15. Environment, Water, and Natural Resources

## Research Workflow

Use this repeatable workflow for each topic.

1. Collect sources.

   Gather credible primary and secondary sources, including government documents, policy papers, datasets, books, speeches, institutional reports, and serious journalism.

2. Extract facts.

   Pull out dates, numbers, actors, institutions, decisions, laws, policies, budgets, and timelines.

3. Structure notes.

   Convert raw material into reusable notes with consistent headings and citations.

4. Analyze.

   Identify incentives, constraints, tradeoffs, bottlenecks, risks, second-order effects, and strategic implications.

5. Compare.

   Compare India with relevant countries, regions, or historical examples.

6. Synthesize.

   Turn notes into briefs, essays, dashboards, timelines, maps, or sector explainers.

7. Update.

   Revisit time-sensitive topics as new data, policies, or events emerge.

## Standard Research Template

Each major topic should use this structure:

- One-line summary
- Why this matters
- Current state
- Historical context
- Key actors and institutions
- Relevant policies, laws, and programs
- Data and indicators
- Strengths
- Bottlenecks
- Global comparison
- Opportunities
- Risks
- Future scenarios
- What India should do next
- Open questions
- Sources

## First 10 Topics

1. First user-submitted dashboard research topic
2. India-China strategic competition
3. India's energy transition
4. Digital public infrastructure and India Stack
5. Defense modernization and domestic manufacturing
6. Agriculture productivity and food security
7. Urbanization and infrastructure finance
8. Education, skills, and demographic dividend
9. Healthcare capacity and public health systems
10. India's role in the Global South

## Pilot Topic

Start with the existing `us-iran-war` archive topic as seed data for local Postgres.

The goal of the pilot is not only to understand that topic. The goal is to test the database import path, source-backed evidence tables, structured topic data, and dashboard presentation pattern before expanding to other sectors or geopolitical questions.

## Output Formats

Project India can produce multiple kinds of outputs:

- Research notes
- Sector explainers
- Policy briefs
- Timelines
- Data tables
- Dashboards
- Long-form essays
- Comparative country studies
- Maps and visual explainers
- AI workflows and prompt libraries

## Integrated System

Project India should be built as an integrated research system.

Core layers:

- Postgres is the living workspace: topics, sources, metrics, timelines, gaps, and run history.
- Markdown and JSON are the curated archive: notes, topic files, sources, briefs, and structured exports.
- Python is the machinery: imports, data processing, timelines, charts, reports, and future automation.
- The Streamlit dashboard is the voice: insight briefs, structured evidence boards, visual explainers, and decision-ready communication.

The default flow is:

Topic idea -> Source-backed evidence -> Postgres tables -> Analysis -> Brief -> Dashboard

The Python package starts small on purpose. It should grow only when a workflow becomes repeated enough to deserve automation.

## Source Standards

- Prefer primary sources when possible.
- Record publication dates and access dates for time-sensitive claims.
- Separate facts, interpretations, and opinions.
- Preserve source links near the claims they support.
- Mark uncertainty clearly.
- Avoid relying on a single source for major claims.
- Revisit claims when new data or policy changes occur.

## Near-Term Plan

1. Keep local Postgres as the working data layer.
2. Migrate the dashboard to read Postgres first.
3. Add a simple local topic intake path that writes to Postgres.
4. Review the dashboard output and improve the database-backed research loop before expanding to other topics.
