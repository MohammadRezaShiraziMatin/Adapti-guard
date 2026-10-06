from dataclasses import dataclass
import re

from adapti_guard.core.models import DefenseAction


@dataclass
class DefenseResult:
    action: DefenseAction
    allowed: bool
    content: str
    tool_access: bool
    reason: str


class DefenseActionLayer:

    def execute(
        self,
        action: DefenseAction,
        content: str,
    ) -> DefenseResult:

        if action == DefenseAction.NO_INTERVENTION:

            return DefenseResult(
                action=action,
                allowed=True,
                content=content,
                tool_access=True,
                reason="no_intervention",
            )

        if action == DefenseAction.SANITIZE:

            sanitized = self._sanitize(content)

            return DefenseResult(
                action=action,
                allowed=True,
                content=sanitized,
                tool_access=True,
                reason="content_sanitized",
            )

        if action == DefenseAction.TOOL_RESTRICTION:

            return DefenseResult(
                action=action,
                allowed=True,
                content=content,
                tool_access=False,
                reason="tool_access_restricted",
            )

        if action == DefenseAction.BLOCK:

            return DefenseResult(
                action=action,
                allowed=False,
                content="",
                tool_access=False,
                reason="interaction_blocked",
            )

        raise ValueError(
            f"Unsupported defense action: {action}"
        )

    def _sanitize(self, content: str) -> str:

        if not content:
            return ""

        sanitized = content.strip()

        remove_patterns = [

            r"\bignore\s+(?:all\s+)?(?:previous|prior)\s+instructions?\b",

            r"\bfollow\s+this\s+instruction\s+instead\b",

            r"\bfollow\s+the\s+following\s+instruction\b",

            r"\breveal\s+(?:your\s+)?system\s+prompt\b",

            r"\bshow\s+(?:me\s+)?(?:your\s+)?system\s+prompt\b",

            r"\bprint\s+(?:your\s+)?system\s+prompt\b",

            r"\bsystem\s+(?:update|message|instruction)\b",

            r"\btrusted\s+(?:system\s+)?instruction\b",

            r"\bhigher\s+priority\b",

            r"\btool\s+(?:result|output)\b",

            r"\btrusted\s+tool\s+output\b",

            r"\bexecute\s+the\s+following\s+instruction\b",

            r"\bprevious\s+security\s+policy\b",

            r"\bsecurity\s+policy\s+(?:was|has\s+been)\s+updated\b",

            r"\bno\s+longer\s+applicable\b",

            r"\bconstraints\s+have\s+been\s+superseded\b",

            r"\bsuperseded\b",

            r"\bsystem\s+(?:has\s+)?authorized\b",

            r"\bsystem\s+authorizes?\b",
        ]

        for pattern in remove_patterns:

            sanitized = re.sub(
                pattern,
                "",
                sanitized,
                flags=re.IGNORECASE,
            )

        sanitized = re.sub(
            r"\s{2,}",
            " ",
            sanitized,
        )

        sanitized = sanitized.strip(
            " ,:;.-"
        ).strip()

        residual_patterns = [

            r"\bsystem\s+prompt\b",
            r"\bprotected\s+information\b",
            r"\bconfidential\b",
            r"\bsecret\b",
            r"\bexfiltrat",
            r"\bexecute\b",
            r"\btrusted\s+tool\b",
            r"\bsystem\s+authoriz",
        ]

        if any(
            re.search(
                pattern,
                sanitized,
                flags=re.IGNORECASE,
            )
            for pattern in residual_patterns
        ):

            return "[SANITIZED]"

        if not sanitized:
            return "[SANITIZED]"

        return sanitized
