# [EXPLORATORY] Downstream exposure procedure (locked before searching beyond the AgentDyn paper itself)
Search: arXiv API all:AgentDyn; DDG / WebSearch "AgentDyn" 2026; GitHub forks/dependents of SaFo-Lab/AgentDyn; Semantic Scholar citations (retry once).
Include: 2026 papers reporting results on any AgentDyn suite (shopping/github/dailylife).
Per paper, from full text (arXiv HTML/PDF): suites, attacks, whether the paper uses tool_knowledge attack or a metric built on ground_truth() (e.g. ground-truth call-based utility/attack metrics, check()).
Classify: EXPOSED = uses tool_knowledge or a ground_truth()-based metric on AgentDyn suites whose GT we found defective (shopping, github, dailylife inj2/6);
NOT EXPOSED = only utility()/security() outcome metrics with attacks that do not read ground_truth();
UNKNOWN = not determinable from text. Section/page refs required. Exposure only; no claims of error.
