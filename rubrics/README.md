# Rubrics

One file per dimension, version 1: `demand_pain`, `competition`, `differentiation`, `feasibility`, `risk`,
`learning`. JSON, so that services and CI read them with the standard library (JSON is also valid YAML, the form
shown in the Guide, section 10). Higher is always better for the student.

Each file holds `dimension`, `version`, `scale`, an anchor for every score 0 to 5, counting `rules`, the computed
`features`, the `output_schema` and one worked example per level. Contract:
`contracts/schemas/rubric.schema.json`. A score cites the rubric as `<dimension>@v<version>`.

Rules:
- A change to a file's content means a new `version` and a new evaluation.
- No evidence means the scorer abstains. Level 0 is a judgment on cards that were found, not on none.
- The worked examples are invented to explain the levels. They are not real ideas, evidence or human labels and
  must not be used as training or evaluation data.
- `feasibility` and `learning` are both scored by the Feasibility scorer, and the Competition scorer emits
  `competition` and `differentiation` (AMB-01, AMB-02 recommendation).

```sh
python -m pytest rubrics -q
```

CI validates the rubric contract against its examples, but no check runs this directory yet.

## Student review (open)
The students own the content. Anchors and examples were drafted by AI and have **not** been reviewed by either
member. Each member records their own review here; nobody records it for them.

| Member | Reviewed version | Date | Changes asked |
|---|---|---|---|
| Abdullah Adnan | | | |
| Asad Ahmed | | | |
