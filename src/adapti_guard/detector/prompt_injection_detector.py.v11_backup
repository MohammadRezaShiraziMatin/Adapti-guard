import re

from src.adapti_guard.core.models import DetectionResult


class PromptInjectionDetector:

    PATTERNS = {
        "ignore_previous_instructions": [
            r"\bignore\s+(all\s+)?(the\s+)?previous\s+(instructions?|tasks?|commands?|directions?|information)\b",
            r"\bignore\s+(all\s+)?(the\s+)?prior\s+(instructions?|tasks?|commands?|directions?)\b",
            r"\bignore\s+(the\s+)?above\s+(instructions?|commands?|directions?)\b",
            r"\bdisregard\s+(all\s+)?(the\s+)?previous\s+(instructions?|tasks?|commands?)\b",
            r"\bdisregard\s+(the\s+)?above\s+(instructions?|commands?)\b",
            r"\bforget\s+(all\s+)?(the\s+)?previous\s+(instructions?|tasks?|information|assignments?)\b",
            r"\bforget\s+everything\b",
            r"\bleave\s+(all\s+)?previous\s+information\s+behind\b",
        ],

        "instruction_override": [
            r"\bnew\s+(instructions?|task|commands?)\b",
            r"\bstart\s+over\b",
            r"\bstart\s+from\s+scratch\b",
            r"\bnew\s+task\b",
            r"\bnow\s+focus\s+on\s+(your\s+)?new\s+task\b",
            r"\boverride\s+(the\s+)?instructions?\b",
            r"\bsuperseded\b",
            r"\bno\s+longer\s+applicable\b",
            r"\bprevious\s+tasks?\b",
            r"\bprevious\s+assignments?\b",
        ],

        "follow_instead": [
            r"\bfollow\s+this\s+instruction\s+instead\b",
            r"\bfollow\s+the\s+following\s+instruction\b",
            r"\binstead\s+(do|output|write|show|provide)\b",
        ],

        "prompt_extraction": [
            r"\b(reveal|show|print|display|output|give)\s+(me\s+)?(your\s+)?(full\s+)?prompt\b",
            r"\b(reveal|show|print|display|output|give)\s+(me\s+)?(your\s+)?system\s+prompt\b",
            r"\bshow\s+(me\s+)?all\s+(your\s+)?prompt\s+texts?\b",
            r"\bcopy\s+(the\s+)?full\s+prompt\b",
            r"\bcopy\s+(the\s+)?prompt\s+text\b",
            r"\bprompt\s+texts?\b",
        ],

        "role_attack": [
            # Explicit role-play requests
            r"\bpretend\s+(you\s+are|to\s+be)\b",
            r"\bact\s+as\s+(an?\s+)?[a-z][a-z0-9_-]*(?:\s+[a-z][a-z0-9_-]*){0,4}\b",
            r"\bplay\s+(the\s+)?role\s+of\b",
            r"\broleplay\b",
            r"\brole[-\s]?play\b",
            r"\bfrom\s+now\s+on\s+you\s+are\b",

            # Identity reassignment with a named/persona target
            r"\bnow\s+you\s+are\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}\b",
            r"\byou\s+are\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}\b",

            # Explicit persona/character framing
            r"\b(?:assume|adopt|take\s+on)\s+(?:the\s+)?(?:role|persona|character)\s+of\b",
            r"\b(?:respond|answer|speak|write)\s+(?:as|like)\s+(?:a|an|the)\b",
        ],

        "authority_impersonation": [
            r"\bsystem\s+(update|message|instruction)\b",
            r"\bsystem\s+authorizes?\b",
            r"\bsystem\s+has\s+authorized\b",
            r"\bhigher\s+priority\b",
            r"\btrusted\s+(system\s+)?instruction\b",
            r"\bdeveloper\s+message\b",
            r"\bdeveloper\s+instruction\b",
        ],

        "tool_context_attack": [
            r"\btool\s+(result|output|response)\b",
            r"\btrusted\s+tool\s+output\b",
            r"\bexecute\s+the\s+following\s+instruction\b",
            r"\binstructions?\s+contained\s+in\s+(this|the)\s+context\b",
        ],

        "jailbreak": [
            r"\bbypass\s+(the\s+)?(safety|security|rules?)\b",
            r"\bdisable\s+(the\s+)?safety\b",
            r"\bdo\s+not\s+follow\s+(the\s+)?rules\b",
            r"\bignore\s+(the\s+)?safety\b",
            r"\bwithout\s+(any\s+)?restrictions?\b",
        ],

        "secret_extraction": [
            r"\breveal\s+(the\s+)?secret\b",
            r"\bshow\s+(me\s+)?confidential\b",
            r"\bexfiltrate\b",
            r"\bhidden\s+instructions?\b",
            r"\bhidden\s+prompt\b",
            r"\bprivate\s+instructions?\b",
        ],
    }

    ATTACK_TYPE_MAP = {
        "ignore_previous_instructions": "PROMPT_INJECTION",
        "instruction_override": "PROMPT_INJECTION",
        "follow_instead": "PROMPT_INJECTION",
        "prompt_extraction": "SYSTEM_PROMPT_EXTRACTION",
        "role_attack": "ROLE_ATTACK",
        "authority_impersonation": "ROLE_ATTACK",
        "tool_context_attack": "CONTEXT_ATTACK",
        "jailbreak": "JAILBREAK",
        "secret_extraction": "SYSTEM_PROMPT_EXTRACTION",
    }

    def detect(self, text: str) -> DetectionResult:
        if not text:
            return DetectionResult(
                injection_probability=0.0,
                indicators=[],
            )

        text_lower = text.lower()
        indicators = []

        # ---------------------------------------------------------
        # Base pattern detection
        # ---------------------------------------------------------
        for category, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    indicators.append(category)
                    break

        # ---------------------------------------------------------
        # Override / instruction manipulation
        # ---------------------------------------------------------
        override_patterns = [
            r"\bignore\s+(all\s+)?(previous|prior|above|earlier)\b",
            r"\bforget\s+(everything|all|your|the)\b",
            r"\bdisregard\s+(all\s+)?(previous|prior|above|earlier)\b",
            r"\bstart\s+over\b",
            r"\bnew\s+(task|instructions?)\b",
            r"\bfrom\s+now\s+on\b",
            r"\bvergiss\s+(alle\s+)?vorherigen\b",
            r"\bignoriere\s+(alle\s+)?vorherigen\b",
        ]

        if any(re.search(p, text_lower) for p in override_patterns):
            if "instruction_override" not in indicators:
                indicators.append("instruction_override")

        # ---------------------------------------------------------
        # Prompt / instruction extraction
        # ---------------------------------------------------------
        extraction_patterns = [
            r"\b(show|reveal|display|print|tell|give|copy)\b.{0,80}"
            r"\b(system\s+prompt|prompt|instructions?)\b",
            r"\bwhat\s+was\s+written\b",
            r"\bwhat\s+is\s+written\s+(above|before|at\s+the\s+beginning)\b",
            r"\bwhat\s+are\s+your\s+(instructions?|rules?)\b",
            r"\bzeige\s+mir\b.{0,80}\bprompt\b",
        ]

        if any(re.search(p, text_lower) for p in extraction_patterns):
            if "prompt_extraction" not in indicators:
                indicators.append("prompt_extraction")

        # ---------------------------------------------------------
        # Output-control manipulation
        # ---------------------------------------------------------
        output_control = bool(
            re.search(
                r"\b(do\s+not|don't|only|just)\b.{0,80}"
                r"\b(output|say|write|respond|answer|print)\b",
                text_lower,
            )
            or re.search(
                r"\b(output|say|write|respond)\s+only\b",
                text_lower,
            )
        )

        # ---------------------------------------------------------
        # Role-play
        # ---------------------------------------------------------
        role_present = "role_attack" in indicators or bool(
            re.search(
                r"\b(pretend|act\s+as|play\s+the\s+role)\b",
                text_lower,
            )
        )

        # Role + suspicious objective
        malicious_role_context = role_present and bool(
            re.search(
                r"\b(evil|unrestricted|unfiltered|hack|break\s+into|"
                r"destroy|kill|bypass|ignore|rules?|instructions?|"
                r"secret|hidden|system|prompt|"
                r"how\s+do\s+you|how\s+can\s+we|"
                r"break\s+into|house|exploit|"
                r"böse|boese|vernichten|zerstören|zerstoeren|"
                r"anweisungen|regeln|geheim|versteckt|"
                r"aufgabe|antworten|schreiben|"
                r"wie\s+verfährt|wie\s+funktioniert)\b",
                text_lower,
            )
        )

        # ---------------------------------------------------------
        # Jailbreak
        # ---------------------------------------------------------
        jailbreak_context = bool(
            re.search(
                r"\b(ignore|forget|disregard)\b.{0,60}"
                r"\b(rules?|safety|restrictions?|limitations?|polic(?:y|ies))\b",
                text_lower,
            )
            or re.search(
                r"\b(bypass|disable|break)\b.{0,40}"
                r"\b(safety|security|rules?|restrictions?)\b",
                text_lower,
            )
            or re.search(
                r"\bwithout\s+(any\s+)?restrictions?\b",
                text_lower,
            )
        )

        if jailbreak_context and "jailbreak" not in indicators:
            indicators.append("jailbreak")

        # ---------------------------------------------------------
        # V16_PATCH: behavioral / structural attack signals
        # ---------------------------------------------------------
        # Detect injection-like behavior when no explicit keyword
        # pattern fires. Signals are intentionally conjunctive to
        # avoid increasing false positives on ordinary requests.

        v16_signal_count = 0

        # 1. Meta-instruction framing:
        # conversational setup + request to perform a new task.
        meta_setup = bool(
            re.search(
                r"\b(?:hello|hey|attention|stop|okay|ok|very\s+well|"
                r"excellent|good|congratulations|now|nun|jetzt|"
                r"sehr\s+gut|ausgezeichnet|hallo)\b",
                text_lower,
            )
        )

        task_request = bool(
            re.search(
                r"\b(?:answer|write|generate|create|compose|provide|"
                r"explain|tell|respond|print|"
                r"beantworte|schreibe|generiere|erstelle|verfasse|"
                r"erkläre|sage|antworte|"
                r"responde|escribe|genera|crea)\b",
                text_lower,
            )
        )

        if meta_setup and task_request and len(text_lower) > 80:
            v16_signal_count += 1

        # 2. Explicit assistant identity / behavioral reassignment.
        identity_reassignment = bool(
            re.search(
                r"\b(?:you\s+are|you\s+will\s+be|"
                r"du\s+bist|du\s+wirst|"
                r"nun\s+bist\s+du|jetzt\s+bist\s+du|"
                r"act\s+as|pretend|fungiere\s+als|"
                r"sei\s+)\b",
                text_lower,
            )
        )

        if identity_reassignment:
            v16_signal_count += 1

        # 3. Character / simulation framing.
        simulation_context = bool(
            re.search(
                r"\b(?:film|movie|scene|character|role|roleplay|"
                r"scenario|simulation|fictional|story|actors?|"
                r"schauspieler|rolle|szene|geschichte|"
                r"figur|charakter)\b",
                text_lower,
            )
        )

        if simulation_context:
            v16_signal_count += 1

        # 4. Instructional persistence / behavioral constraints.
        persistence_signal = bool(
            re.search(
                r"\b(?:always|never|every\s+time|from\s+now\s+on|"
                r"only|just|stay\s+in|do\s+not\s+break|"
                r"immer|niemals|jedes\s+mal|von\s+jetzt\s+an|"
                r"nur|bleib|bleiben|"
                r"start\s+all|begin\s+all)\b",
                text_lower,
            )
        )

        if persistence_signal:
            v16_signal_count += 1

        # 5. Explicit output / execution objective.
        execution_objective = bool(
            re.search(
                r"\b(?:execute|print|output|return|generate|"
                r"write|respond|answer|"
                r"ausführen|ausgabe|ausgeben|schreiben|"
                r"antworten|beantworten|generieren)\b",
                text_lower,
            )
        )

        if execution_objective:
            v16_signal_count += 1

        # ---------------------------------------------------------
        # V17_PATCH: precision-oriented contextual gating
        # ---------------------------------------------------------
        # Generic task requests are common in benign prompts.
        # Therefore, behavioral signals only become an attack signal
        # when at least one strong injection context is present.

        v17_strong_context = bool(
            re.search(
                r"\b(?:ignore|disregard|forget|override|bypass|"
                r"drop|change|replace|modify|"
                r"ignoriere|vergiss|überspringe|umgehe|"
                r"anweisungen|vorherigen|bisherigen|"
                r"previous|prior|above|rules?|safety|"
                r"system\s+prompt|hidden\s+prompt|"
                r"developer\s+(?:message|instruction))\b",
                text_lower,
                re.DOTALL,
            )
        )

        v17_role_context = bool(
            re.search(
                r"\b(?:you\s+are|now\s+you\s+are|"
                r"from\s+now\s+on\s+you\s+are|"
                r"pretend|act\s+as|play\s+the\s+role|"
                r"du\s+bist|nun\s+bist\s+du|"
                r"jetzt\s+bist\s+du|fungiere\s+als|"
                r"stell\s+dir\s+vor)\b",
                text_lower,
            )
        )

        v17_extraction_context = bool(
            re.search(
                r"\b(?:prompt|system\s+prompt|hidden\s+prompt|"
                r"secret|instructions?|rules?|"
                r"vollständigen\s+prompt|prompt-text)\b",
                text_lower,
            )
            and re.search(
                r"\b(?:show|reveal|print|display|output|give|tell|"
                r"copy|zeigen|zeige|ausgeben|vorzeigen|"
                r"anzeigen|kopieren)\b",
                text_lower,
            )
        )

        v17_output_context = bool(
            re.search(
                r"\b(?:only|just|always|never|"
                r"nur|immer|niemals)\b",
                text_lower,
            )
            and re.search(
                r"\b(?:respond|answer|output|say|write|return|"
                r"antworten|ausgeben|schreiben|sagen)\b",
                text_lower,
            )
        )

        # Strong contextual combinations.
        v17_attack = (
            (v17_strong_context and task_request)
            or (v17_role_context and task_request)
            or (v17_extraction_context)
            or (v17_output_context and v16_signal_count >= 2)
        )

        if v17_attack:
            if "contextual_attack" not in indicators:
                indicators.append("contextual_attack")

        # ---------------------------------------------------------
        # Scoring
        # ---------------------------------------------------------

        # ---------------------------------------------------------
        # V11_PATCH: contextual multilingual injection detection
        # ---------------------------------------------------------

        # Instruction reset / override.
        v11_override_patterns = [
            # English
            r"\bforget\s+(?:everything|all|the\s+above)\b",
            r"\bdisregard\s+(?:everything|all|the\s+above|previous|prior)\b",
            r"\bignore\s+(?:everything|all|the\s+above|previous|prior)\b",
            r"\bstart\s+over\s+with\s+a\s+new\s+(?:task|instruction)\b",

            # German
            r"\bvergiss\s+alles\s+davor\b",
            r"\bvergiss\s+alles\b",
            r"\bvergiss\s+alle\s+(?:aufträge|anweisungen)\b",
            r"\bignoriere\s+alles\s+davor\b",
            r"\bignoriere\s+alle\s+vorherigen\s+(?:anweisungen|befehle)\b",
            r"\bignoriere\s+alle\s+vorangehenden\s+(?:anweisungen|befehle)\b",

            # Spanish
            r"\bolvida\s+todo\b",
            r"\bolvide\s+todo\b",
            r"\bolvida\s+todo\s+lo\s+que\b",
            r"\bolvide\s+todo\s+lo\s+que\b",
            r"\bignora\s+(?:todo|todas\s+las\s+instrucciones)\b",
        ]

        if any(re.search(x, text_lower) for x in v11_override_patterns):
            if "ignore_previous_instructions" not in indicators:
                indicators.append("ignore_previous_instructions")

        # Role reassignment.
        v11_role_patterns = [
            r"\bnow\s+you\s+are\b",
            r"\bokay[,.]?\s+now\s+you\s+are\b",
            r"\bfrom\s+now\s+on\s+you\s+are\b",
            r"\bpretend\s+you\s+are\b",
            r"\bpretend\s+to\s+be\b",
            r"\bact\s+as\b",
            r"\bplay\s+the\s+role\s+of\b",

            # German
            r"\bjetzt\s+bist\s+du\b",
            r"\bnun\s+bist\s+du\b",
            r"\bstell\s+dir\s+vor[,.]?\s+du\s+bist\b",
            r"\bdu\s+bist\b",
        ]

        if any(re.search(x, text_lower) for x in v11_role_patterns):
            if "role_attack" not in indicators:
                indicators.append("role_attack")

        # Output restriction / forced response format.
        v11_output_patterns = [
            r"\bonly\s+output\b",
            r"\bonly\s+say\b",
            r"\bjust\s+say\b",
            r"\brespond\s+only\s+with\b",
            r"\bonly\s+respond\s+with\b",
            r"\bdo\s+not\s+answer\b.*\boutput\b",
            r"\bdo\s+not\s+respond\b.*\boutput\b",
        ]

        if any(re.search(x, text_lower) for x in v11_output_patterns):
            if "instruction_override" not in indicators:
                indicators.append("instruction_override")


        # ---------------------------------------------------------
        # V12_PATCH: contextual task / role / extraction signals
        # ---------------------------------------------------------

        # Task-oriented instruction language.
        v12_task_patterns = [
            # English
            r"\b(?:please\s+)?(?:answer|write|generate|create|compose|provide|tell|explain)\b",
            r"\b(?:your|the)\s+(?:task|job)\s+is\b",
            r"\bhelp\s+me\s+(?:with|write|create|generate)\b",

            # German
            r"\b(?:beantworte|schreibe|verfasse|erstelle|generiere|erkläre|sage)\b",
            r"\b(?:deine|die)\s+(?:aufgabe|aufgabenstellung)\b",
            r"\b(?:hilf|helfen)\s+.*\b(?:schreiben|erstellen|generieren)\b",

            # Spanish
            r"\b(?:responde|escribe|genera|crea|dime|explica)\b",
        ]

        v12_task_present = any(
            re.search(x, text_lower) for x in v12_task_patterns
        )

        # Role reassignment becomes meaningful when it controls
        # the assistant's behavior or is attached to a task.
        v12_role_reassignment = bool(
            re.search(
                r"\b(?:now|from\s+now\s+on)\s+you\s+are\b",
                text_lower,
            )
            or re.search(
                r"\b(?:okay|ok)[,.]?\s+now\s+you\s+are\b",
                text_lower,
            )
            or re.search(
                r"\b(?:jetzt|nun)\s+bist\s+du\b",
                text_lower,
            )
        )

        if v12_role_reassignment and v12_task_present:
            if "role_attack" not in indicators:
                indicators.append("role_attack")

        # Explicit forced-output behavior.
        v12_output_control = bool(
            re.search(
                r"\b(?:only|just)\s+(?:output|say|respond|return)\b",
                text_lower,
            )
            or re.search(
                r"\brespond\s+only\s+with\b",
                text_lower,
            )
            or re.search(
                r"\b(?:nur|einfach)\s+(?:ausgeben|sagen|antworten)\b",
                text_lower,
            )
        )

        if v12_output_control:
            if "instruction_override" not in indicators:
                indicators.append("instruction_override")

        # Contextual extraction request.
        v12_extraction = bool(
            re.search(
                r"\b(?:what\s+was\s+written|tell\s+me|show\s+me|"
                r"give\s+me|print|reveal)\b.*\b"
                r"(?:prompt|instructions?|system\s+prompt|"
                r"beginning|full|complete)\b",
                text_lower,
            )
        )

        if v12_extraction:
            if "prompt_extraction" not in indicators:
                indicators.append("prompt_extraction")


        # ---------------------------------------------------------
        # V13 contextual attack detection
        # ---------------------------------------------------------

        v13_patterns = [
            # English instruction override / reset
            r"\bignore\s+(?:all\s+)?(?:previous|prior|above)\s+(?:instructions?|commands?|rules?)\b",
            r"\bforget\s+(?:everything|all|the\s+above|what\s+i\s+said)\b",
            r"\bdisregard\s+(?:everything|all|the\s+above|previous|prior)\b",
            r"\bstart\s+(?:over|from\s+scratch)\b.*\b(?:new\s+task|instruction)\b",

            # German
            r"\bvergiss\s+(?:alles|alle\s+vorherigen|alle\s+vorangegangenen|alle\s+aufträge)\b",
            r"\bignoriere\s+(?:alles|alle\s+vorherigen|alle\s+vorangegangenen)\b",
            r"\bvergiss\s+alles\s+davor\b",
            r"\bdie\s+obigen\s+ausführungen\s+ignorieren\b",

            # Spanish
            r"\bolvide\s+todo\b",
            r"\bolvida\s+todo\b",
            r"\bignora\s+(?:todo|todas\s+las\s+instrucciones)\b",

            # Role reassignment + task
            r"\bnow\s+you\s+are\b.*\b(?:answer|respond|write|say|explain|describe|tell)\b",
            r"\bokay[,.]?\s+now\s+you\s+are\b.*\b(?:answer|respond|write|say|explain)\b",
            r"\byou\s+are\b.*\bwhat\s+do\s+you\s+think\b",
            r"\byou\s+are\b.*\bhow\s+do\s+you\b",
            r"\bpretend\s+you\s+are\b.*\b(?:how|what|write|answer|respond|say)\b",
            r"\bact\s+as\b.*\b(?:answer|respond|write|say|explain)\b",

            # Character persistence / role-play injection
            r"\bstay\s+(?:in|within)\s+(?:your|the)\s+role\b",
            r"\bdo\s+not\s+break\s+character\b",
            r"\bstay\s+fully\s+in\s+(?:your|the)\s+role\b",

            # Prompt / system extraction
            r"\b(?:show|reveal|give|print|tell)\s+(?:me\s+)?(?:your\s+)?(?:system|hidden|secret)\s+prompt\b",
            r"\bwhat\s+(?:was|is)\s+(?:written|contained)\s+(?:at|in)\s+(?:the\s+)?(?:beginning|prompt)\b",
            r"\b(?:show|reveal|tell)\s+(?:me\s+)?your\s+(?:instructions|rules)\b",

            # Output hijacking
            r"\bonly\s+(?:output|say|respond|return)\s+(?:the\s+)?following\b",
            r"\brespond\s+only\s+with\b",
            r"\bonly\s+respond\s+with\b",
        ]

        v13_hits = []

        for pattern in v13_patterns:
            if re.search(pattern, text_lower, re.DOTALL):
                v13_hits.append(pattern)

        if v13_hits:
            if "contextual_attack" not in indicators:
                indicators.append("contextual_attack")

            # Strong reset/override attacks
            if any(
                x in text_lower
                for x in [
                    "ignore all previous",
                    "ignore previous",
                    "vergiss alles",
                    "vergiss alles davor",
                    "ignoriere alle vorherigen",
                    "ignoriere alles",
                    "olvide todo",
                    "forget everything",
                ]
            ):
                score_boost = 0.45

            # Role/task and prompt extraction
            elif len(v13_hits) >= 1:
                score_boost = 0.30

            else:
                score_boost = 0.25

            v13_score_boost = score_boost
        else:
            v13_score_boost = 0.0

        # ---------------------------------------------------------
        # V15_PATCH: contextual combination scoring
        # ---------------------------------------------------------
        # Detect attacks whose meaning emerges from combinations of
        # signals rather than a single keyword.
        #
        # Important:
        #   - Do NOT score generic task verbs by themselves.
        #   - Require contextual attack framing.
        #   - Preserve the existing low false-positive behavior.

        v15_score = 0.0

        # Role reassignment + task/objective.
        if (
            role_present
            and v12_task_present
            and (
                v12_role_reassignment
                or re.search(
                    r"\b(?:pretend|act\s+as|play\s+the\s+role|"
                    r"du\s+bist|nun\s+bist\s+du|jetzt\s+bist\s+du)\b",
                    text_lower,
                )
            )
        ):
            v15_score = max(v15_score, 0.30)

        # Fictional / simulated context + actionable request.
        fictional_context = bool(
            re.search(
                r"\b(?:film|movie|scene|fictional|fiction|story|"
                r"roleplay|scenario|character|schauspieler|"
                r"filmfigur|geschichte|szene)\b",
                text_lower,
            )
        )

        actionable_context = bool(
            re.search(
                r"\b(?:how\s+do\s+you|how\s+can\s+we|"
                r"generate|write|create|execute|tell|show|"
                r"wie\s+bricht|wie\s+funktioniert|"
                r"wie\s+verfährt|schreibe|erstelle|generiere|"
                r"ausführen|zeigen)\b",
                text_lower,
            )
        )

        if fictional_context and actionable_context:
            v15_score = max(v15_score, 0.30)

        # Reset/override + a subsequent task.
        reset_signal = bool(
            re.search(
                r"\b(?:ignore|disregard|forget|drop|"
                r"ignoriere|vergiss|vergesse|"
                r"ignorieren|vergessen)\b",
                text_lower,
            )
            and re.search(
                r"\b(?:instructions?|rules?|previous|prior|above|"
                r"anweisungen|regeln|vorherigen|bisherigen|"
                r"aufgaben|information)\b",
                text_lower,
            )
        )

        new_task_signal = bool(
            re.search(
                r"\b(?:now|instead|then|new|following|"
                r"nun|jetzt|stattdessen|folgende|neue)\b",
                text_lower,
            )
            and v12_task_present
        )

        if reset_signal and new_task_signal:
            v15_score = max(v15_score, 0.45)

        # Prompt/system extraction + forced output.
        if (
            "prompt_extraction" in indicators
            and output_control
        ):
            v15_score = max(v15_score, 0.50)

        # Explicit instruction to replace/change the assistant's
        # behavior, even when the exact override vocabulary is absent.
        behavior_change = bool(
            re.search(
                r"\b(?:change|replace|modify|rewrite|"
                r"follow|switch|respond|answer)\b.{0,100}"
                r"\b(?:instructions?|rules?|behavior|"
                r"every\s+time|always|instead)\b",
                text_lower,
                re.DOTALL,
            )
        )

        if behavior_change and v12_task_present:
            v15_score = max(v15_score, 0.30)

        score = 0.0

        for indicator in indicators:
            if indicator == "ignore_previous_instructions":
                score += 0.45
            elif indicator == "prompt_extraction":
                score += 0.45
            elif indicator in {
                "jailbreak",
                "authority_impersonation",
                "secret_extraction",
            }:
                score += 0.35
            elif indicator == "role_attack":
                if malicious_role_context:
                    score += 0.35
            elif indicator == "instruction_override":
                score += 0.30
            else:
                score += 0.25

        if output_control:
            score += 0.30

        if malicious_role_context:
            score += 0.15

        if len(indicators) >= 2:
            score += 0.10

        if v13_score_boost > 0.0:
            score = max(score, v13_score_boost)

        if v15_score > 0.0:
            score = max(score, v15_score)

        score = min(score, 1.0)

        return DetectionResult(
            injection_probability=round(score, 3),
            indicators=indicators,
        )

    def metadata(self, detection: DetectionResult) -> dict:
        attack_types = []

        for indicator in detection.indicators:
            attack_type = self.ATTACK_TYPE_MAP.get(
                indicator,
                "PROMPT_INJECTION",
            )

            if attack_type not in attack_types:
                attack_types.append(attack_type)

        if not attack_types:
            attack_type = "NONE"
        elif len(attack_types) == 1:
            attack_type = attack_types[0]
        else:
            attack_type = "MULTI_ATTACK"

        return {
            "is_injection": detection.injection_probability >= 0.25,
            "confidence": detection.injection_probability,
            "matches": list(detection.indicators),
            "attack_type": attack_type,
            "attack_types": attack_types,
        }
