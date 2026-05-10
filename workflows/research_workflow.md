# Research Workflow

This workflow turns a broad question into structured notes, evidence, analysis, and outputs.

## 1. Frame the Question

Start with a question that can be researched.

Good format:

- What is happening?
- Why does it matter?
- Who are the actors?
- What constraints shape their choices?
- What could happen next?

## 2. Collect Sources

Before searching the web or calling an AI model, audit what the repository
already knows:

```bash
python3 -m project_india.cli index-research
python3 -m project_india.cli plan-research "<Topic>" --slug <topic-slug> --category <category>
```

Use the generated research plan to decide whether deep research is needed. This
keeps API spending focused on gaps rather than re-researching existing notes.

Gather sources in this order:

1. Primary sources: government documents, laws, budgets, speeches, official datasets.
2. Institutional sources: think tanks, multilateral institutions, universities, industry bodies.
3. Serious journalism and expert commentary.
4. Books and long-form historical material.

Record sources in `sources/<topic>-sources.md`.

## 3. Extract Facts

Pull out:

- Dates
- Policies
- Budgets
- Institutions
- People and organizations
- Data points
- Milestones
- Contradictions
- Claims that need verification

## 4. Structure the Topic Note

Use the standard topic structure in `docs/research-notes/project-roadmap.md`.

Keep facts close to sources. Mark uncertainty clearly.

## 5. Analyze

Look for:

- Incentives
- Bottlenecks
- Tradeoffs
- Institutional capacity
- Political economy
- Strategic risks
- Second-order effects
- Comparison with other countries

## 6. Produce Outputs

Each mature topic can produce:

- Sector note
- Source log
- Brief
- Timeline
- Data table
- Presentation outline
- Dashboard or chart

## 7. Review and Update

Before publishing or relying on a conclusion:

- Check dates.
- Confirm sources.
- Separate facts from interpretation.
- Note open questions.
- Update when new policy or data arrives.
