"""
question_classifier.py
Classifies incoming messages into the GameReady AI domains.

CATEGORY FLOW:
  PROJECT   — platform-specific questions answered from GameReady data.
  GAMING    — general PC/gaming questions answered by OpenRouter.
  UNRELATED — anything outside gaming or the GameReady platform.

Project questions are further classified into compatibility, upgrade,
recommendation, profile, and greeting intents.
"""
from __future__ import annotations
import re
from enum import Enum


class QuestionCategory(str, Enum):
    PROJECT = "project"
    GAMING = "gaming"
    UNRELATED = "unrelated"


class QuestionType(str, Enum):
    COMPATIBILITY  = "compatibility"
    UPGRADE        = "upgrade"
    RECOMMENDATION = "recommendation"
    PROJECT_REVIEW = "project_review"
    PROFILE        = "profile"
    GREETING       = "greeting"
    GENERAL        = "general"
    DISALLOWED     = "disallowed"


# ---------------------------------------------------------------------------
# ALLOWED patterns — GameReady domain
# ---------------------------------------------------------------------------

_COMPAT_PATTERNS = [
    r"\bcan (i|my (pc|computer|system|laptop|rig)) run\b",
    r"\bwill (it|this|my (pc|gpu|system)) run\b",
    r"\bcan (i|my) play\b",
    r"\bis .+ compatible\b",
    r"\bcompatibility\b",
    r"\bcan it run\b",
    r"\bfps\b",
    r"\bframes? per second\b",
    r"\bframerate\b",
    r"\bperformance (for|on|in)\b",
    r"\bhow (well|smooth)\b",
    r"\bwhat (settings?|graphics?) (for|on|in|will)\b",
    r"\b(run|play) .+ on my\b",
    r"\bmin(imum)? (req|spec)\b",
    r"\brec(ommended)? (req|spec)\b",
    r"\bgame requirements\b",
]

_UPGRADE_PATTERNS = [
    r"\bupgrade\b",
    r"\bbottleneck(ing)?\b",
    r"\bimprove (fps|performance|gaming)\b",
    r"\bwhat (should|do) i (upgrade|buy|replace|change)\b",
    r"\bwhich (component|part|hardware) (should|to)\b",
    r"\bget better (fps|performance)\b",
    r"\bbetter (gpu|cpu|ram|graphics card|processor)\b",
    r"\bnew (gpu|cpu|graphics card|processor|ram)\b",
    r"\bmy (gpu|cpu|ram) is (bad|weak|slow|old|limiting)\b",
    r"\b(weak|slow|limiting|outdated) (gpu|cpu|ram|hardware)\b",
    r"\bshould i (upgrade|buy|replace)\b",
]

_RECOMMENDATION_PATTERNS = [
    r"\brecommend\b",
    r"\bsuggest\b",
    r"\bwhat (games?|titles?) (can|should|will) (i|my)\b",
    r"\bgames? for my (pc|system|specs?|rig)\b",
    r"\bwhat (should|can) i play\b",
    r"\bshow .+ games?\b",
    r"\bshow (me )?(games?|titles?)\b",
    r"\b(compatible|playable) games?\b",
    r"\bgames? (i|that) can run\b",
    r"\bgames? (i can|my (pc|system) can)\b",
    r"\bwhat('s| is) good (for|on) my\b",
    r"\bgive me (some|a few) (games?|titles?)\b",
    r"\blist (of )?games?\b",
    r"\bsimilar games?\b",
    r"\bwhat (games?|titles?) (do you have|are in|are available)\b",
    r"\bgameready (library|games?|catalog)\b",
]

_PROFILE_PATTERNS = [
    r"\bmy (gaming )?profile\b",
    r"\bkind of gamer\b",
    r"\bgamer (type|style|am i)\b",
    r"\bwhat genres? (do i|i)\b",
    r"\bmy (favorite|fav|preferred) genres?\b",
    r"\bmy gaming (habits?|history|stats?|style)\b",
    r"\b(inspect|check|review|evaluate) (my|the) (pc|system|rig|build)\b",
    r"\b(analyze|analyse|tell me about) my (system|specs?|gaming)\b",
    r"\bmy system (strengths?|weaknesses?|overview|specs?)\b",
    r"\bhow (good|powerful|strong) (is )?my (pc|system|rig|specs?)\b",
    r"\bhow (is|does) my (pc|system|rig|build)\b",
    r"\brate my (pc|system|rig|build)\b",
    r"\bmy (cpu|gpu|ram|storage|hardware)\b",
    r"\bwhat (is|are) my (specs?|hardware|system)\b",
    r"\bmy scan (history|results?)\b",
    r"\bmy compatibility (history|results?|scores?)\b",
    r"\bmy (favorites?|favourite games?)\b",
]

_GREETING_PATTERNS = [
    r"^(hi|hello|hey|hiya|howdy|greetings)[!.,]?$",
    r"^(hi|hello|hey) (there|gameready)[!.,]?$",
    r"^what can you (do|help with)\??$",
    r"^help\??$",
    r"^(good morning|good afternoon|good evening)[!.,]?$",
]
_PROJECT_PATTERNS = [
    r"\bmy project\b",
    r"\breview (my|the) (project|repo|repository)\b",
    r"\binspect (my|the) (project|repo|repository)\b",
    r"\bscan (my|the) (project|repo|repository)\b",
    r"\babout my project\b",
    r"\b(what is|tell me about) (my|the) project\b",
]
_GAMING_PATTERNS = [
    r"\bwhat is (dlss|ray tracing|vram|gpu|cpu|vulkan|directx|shader|path tracing)\b",
    r"\bexplain (dlss|ray tracing|vram|ray tracing|fps|vr|gpu|cpu|gpu architecture|ray tracing)\b",
    r"\bcompare .+ (vs|versus|and) .+\b",
    r"\bbest (action|rpg|shooter|racing|strategy|adventure|simulation|sports) games\b",
    r"\brecommend (racing|action|rpg|shooter|adventure|strategy|simulation) games\b",
    r"\bwhat are the requirements for\b",
    r"\bwhat does .+ mean\b",
    r"\bwhat is high refresh rate\b",
    r"\bshould i use (dlss|ray tracing|hdr)\b",
    r"\bhow many fps\b",
    r"\bwhat is the difference between\b",
    r"\bcompare (rtx|gtx|rx|radeon|ryzen|core)\b",
]
# ---------------------------------------------------------------------------
# DISALLOWED — explicit blocklist patterns
# These are checked LAST; anything not matched above falls here too.
# ---------------------------------------------------------------------------

_DISALLOWED_PATTERNS = [
    # General non-gaming blocklist (keep unrelated topics blocked)
    # People / celebrities
    r"\b(who is|tell me about) (cristiano|messi|ronaldo|elon|trump|biden|celebrities?)\b",
    r"\bwho (invented|created|made|founded)\b",
    # Code / math / writing
    r"\b(write|generate|create|give me) (a |some )?(python|javascript|java|code|script|function|program|class)\b",
    r"\bsolve\b.*(equation|problem|math)\b",
    r"\b(calculate|compute|find)\b.*(sum|product|integral|derivative|factorial)\b",
    r"\bwrite (a |an )?(essay|story|poem|joke|letter|email|report)\b",
    # Jokes / trivia / general chat
    r"\btell me a joke\b",
    r"\bfunny\b",
    r"\bwhat('s| is) the weather\b",
    r"\btoday('s)? (date|time|weather|news)\b",
    r"\btranslate\b",
    r"\b(world war|history of|ancient|medieval|renaissance)\b",
    r"\b(politics|election|president|prime minister|government)\b",
    r"\b(recipe|cook|ingredient|food)\b",
    r"\b(movie|film|actor|actress|director)\b",
    r"\b(song|music|artist|band|album)\b",
    r"\b(sport|football|soccer|cricket|basketball|baseball)\b.*(?<!gaming)",
    r"\b(stock|crypto|bitcoin|invest|finance|economy)\b",
]


def _matches(text: str, patterns: list[str]) -> bool:
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


def classify(message: str) -> QuestionType:
    """
    Return the QuestionType for *message*.

    Order matters:
      1. Check allowed GameReady categories first
      2. Check greetings
      3. Check explicit disallowed patterns
      4. Anything unrecognised → DISALLOWED (strict mode)
    """
    msg = message.strip()

    # --- ALLOWED ---
    if _matches(msg, _COMPAT_PATTERNS):
        return QuestionType.COMPATIBILITY

    if _matches(msg, _UPGRADE_PATTERNS):
        return QuestionType.UPGRADE

    if _matches(msg, _RECOMMENDATION_PATTERNS):
        return QuestionType.RECOMMENDATION

    if _matches(msg, _PROFILE_PATTERNS):
        return QuestionType.PROFILE

    if _matches(msg, _PROJECT_PATTERNS):
        return QuestionType.PROJECT_REVIEW

    if _matches(msg, _GREETING_PATTERNS):
        return QuestionType.GREETING

    if _matches(msg, _GAMING_PATTERNS):
        return QuestionType.GENERAL

    # --- DISALLOWED (explicit + catch-all) ---
    # Everything not explicitly in the GameReady domain is blocked
    return QuestionType.DISALLOWED


def classify_category(message: str) -> QuestionCategory:
    """Return the top-level GameReady question category."""
    msg = message.strip()

    if _matches(msg, _DISALLOWED_PATTERNS):
        return QuestionCategory.UNRELATED

    if _matches(msg, _COMPAT_PATTERNS + _UPGRADE_PATTERNS + _RECOMMENDATION_PATTERNS + _PROFILE_PATTERNS + _GREETING_PATTERNS + _PROJECT_PATTERNS):
        return QuestionCategory.PROJECT

    if _matches(msg, _GAMING_PATTERNS):
        return QuestionCategory.GAMING

    return QuestionCategory.UNRELATED


__all__ = ["QuestionCategory", "QuestionType", "classify", "classify_category"]
