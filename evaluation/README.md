# Evaluation Benchmark

The benchmark contains five intentionally bounded SRE failure scenarios.

## Metrics

- **Root-cause accuracy:** whether the top RCA matches the expected cause.
- **Evidence relevance:** whether the cited evidence actually supports the RCA.
- **Grounding violations:** references to evidence IDs that do not exist.
- **Structured-output validity:** whether the investigation result passes Pydantic validation.
- **Failure transparency:** whether missing or contradictory evidence is surfaced as a limitation.

## Procedure

1. Run each scenario with its incident context and supplied evidence.
2. Record the top root cause and confidence.
3. Check every cited evidence ID against the collected evidence.
4. Mark root-cause accuracy as correct / partial / incorrect.
5. Record grounding violations and structured-output failures.
6. Summarize results in the project README.

The benchmark is deliberately small for the internship MVP; it is intended to demonstrate evaluation methodology rather than claim production-grade reliability.
