@promplet version: 0.7

@module weavemark.domains.research.news_event_triage

# News and Event Triage

@note
  Reusable triage layer for deciding whether a discovered item belongs in a
  recurring news or events digest.

Use this layer after web search and crawling have found candidate items.

## Shared triage obligations

- Include only items relevant to the exact topic, audience, geography, timing,
  and mode.
- Deduplicate the same underlying item across many sources.
- Rank by user relevance, novelty, evidence quality, timeliness, and practical
  actionability.
- Separate high-confidence items from tentative leads.
- Preserve source links and cite the strongest source for each item.
- Surface safety, eligibility, access, cost, location, age, or scheduling
  constraints when they affect whether the user should act.

## News mode

For news, prioritize:

- material developments in the lookback window;
- official announcements and primary documents;
- credible reporting with named entities and dates;
- analysis that explains why the development matters;
- contradictory evidence or skepticism that changes interpretation.

Avoid:

- generic explainers with no new development;
- SEO posts, duplicate syndicated stories, and thin commentary;
- claims that cannot be traced to a credible source.

## Events mode

For events, prioritize:

- upcoming or current events inside the requested window;
- official event pages, venue calendars, organizer pages, and local calendars;
- age-appropriate, accessible, practical options;
- date, time, location, cost, booking, cancellation, and safety details;
- alternatives for different weather, energy level, budget, or distance.

Avoid:

- past events unless they recur and the next date is clear;
- vague activity ideas without a source or availability;
- items unsuitable for the user's age, constraints, or location.
