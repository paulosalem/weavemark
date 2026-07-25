They should **not build the feature-rich prototype**. Option **B** is too broad for 3 engineers in 6 weeks and is likely to produce something impressive-looking but hard to adopt, hard to sell, and unfinished.

The best default choice is:

## Choose C: CLI tool + API, aimed at technical early adopters

This maximizes the chance of getting paying customers **if the target customers can use developer-facing tools**.

Allocate the 3 engineers as follows:

1. **Engineer 1: Core API / backend**
   - Build the minimum valuable workflow.
   - Focus on reliability, authentication, basic billing/pilot access, logging, and integration points.
   - Avoid extra features.

2. **Engineer 2: CLI / integration layer**
   - Build a simple CLI that exposes the core value quickly.
   - Make setup fast.
   - Include examples, templates, and common use-case commands.

3. **Engineer 3: Activation, docs, onboarding, customer support**
   - Write docs and quickstart guides.
   - Create demo scripts and sample projects.
   - Help early customers integrate.
   - Collect feedback and convert pilots into paid usage.

The goal should not be “ship the most product.” The goal should be:

> Get a narrow group of customers to experience the core value quickly enough that they are willing to pay.

If the startup’s customers are **nontechnical business users**, then option C is too high-friction. In that case, they should choose a very narrow version of **A**: one polished web workflow, not a broad product.

But given the constraints and assuming technical early adopters are viable, the strongest allocation is **C: API + CLI + onboarding/docs**.

ANSWER: 3
