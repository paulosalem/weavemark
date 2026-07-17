@promplet version: 0.7

@module weavemark.domains.work_intelligence.topic_intelligence_monitor

# Topic Intelligence Monitor

@refine module:weavemark.domains.research.recurring_topic_monitor mingle: true
@refine module:weavemark.domains.research.news_event_triage mingle: true

@note
  Reusable domain layer for applications that follow selected topics, detect
  meaningful signals, and warn the user when something is worth attention.

Use this layer when a product must convert ongoing news, research, releases,
events, announcements, discussions, or other external signals into structured
work intelligence for a specific person, team, or project.

## Monitored topics and interest profile

- Define user-selected topics, subtopics, exclusions, regions, organizations,
  people, projects, products, markets, technologies, or communities to follow.
- Let each topic carry intent: watch for risks, opportunities, deadlines,
  competitor movement, funding, product releases, regulation, research, events,
  or project-relevant ideas.
- Support source-family preferences and exclusions. Source families may include
  official pages, feeds, newsletters, journals, repositories, social posts,
  community forums, calendars, press releases, podcasts, videos, and saved files.
- Preserve why the topic matters to the user's work so future summaries and
  alerts can explain relevance, not just mention matching keywords.

## Signal capture and triage

- A signal MUST keep provenance: source, title, author or organization when
  known, URL or local reference, retrieved time, published time, and evidence
  quality.
- Deduplicate repeated coverage of the same underlying event or idea.
- Score signals by relevance, novelty, freshness, confidence, urgency,
  potential impact, and actionability.
- Separate confirmed facts, reported claims, opinions, forecasts, rumors,
  repeated background, and speculative leads.
- Preserve rejected or muted signals when that history improves future filtering.

## Alerts, warnings, and digests

- Alerts MUST explain why the item matters, what changed, confidence level, and
  what the user can do next.
- Warnings SHOULD trigger for user-defined watch conditions such as deadline
  proximity, high-impact news, sudden topic activity, competitor movement,
  funding, security or reliability concerns, policy changes, or project blockers.
- Digests SHOULD group items by topic, source family, urgency, decision impact,
  and suggested follow-up.
- Notification noise MUST be controllable through thresholds, mute rules,
  feedback, and digest cadence.

## Feedback loop

- The user MUST be able to mark a signal as useful, irrelevant, duplicate,
  already handled, watch later, or converted into action.
- Feedback SHOULD adjust future relevance and alert behavior without hiding
  provenance or making irreversible filtering decisions.
- The system SHOULD track whether a signal eventually led to a decision,
  delegation, artifact, project change, or discarded idea.
