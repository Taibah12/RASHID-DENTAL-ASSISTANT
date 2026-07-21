import re

class SafetyGuardrails:
    """
    Analyzes raw user input to protect against prompt-injection attempts
    and restrict premature medical diagnostics.
    """
    
    # Patterns showing clear intent to override system constraints
    INJECTION_PATTERNS = [
        r"(?i)ignore\s+(your\s+)?(previous|prior|system|instructions|rules)",
        r"(?i)you\s+are\s+now\s+a\s+(developer|unrestricted|jailbreak)",
        r"(?i)reveal\s+(your\s+)?(system\s+prompt|instructions|secret|api)",
        r"(?i)output\s+the\s+above\s+text\s+verbatim",
        r"(?i)override\s+safety\s+protocols"
    ]

    @classmethod
    def detect_prompt_injection(cls, user_input: str) -> bool:
        """Returns True if user input matches injection patterns."""
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, user_input):
                return True
        return False