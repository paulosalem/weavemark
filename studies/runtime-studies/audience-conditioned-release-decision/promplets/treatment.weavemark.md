@refine module:weavemark.std.guidelines.evidence_quality
@refine module:weavemark.std.lenses.decision_gate

# Release decision
Should we release @{release}?

# Audience requirements
  @match @{audience}
      "Implementation Team" ==>
          Emphasize architecture, interfaces, failure modes, and test evidence.

      "Release Team" ==>
          Emphasize readiness criteria, user impact, operational risks, and rollback options.

# Development notes
@{dev_notes}

@output enforce: strict
  Return the decision, evidence, risks, and next action.
