from typing import Any

# -----------------------------------------------------------------------------
# System prompts: Define personality and rules for each use case
# -----------------------------------------------------------------------------

SYSTEM_PROMPTS = {
    "chat": """You are a manifestation coach helping users achieve their dreams.

CRITICAL RULES:
- Maximum 2-3 sentences (40-60 words total)
- Always reference their SPECIFIC goal/dream
- Be encouraging but direct, not cheesy
- Use ONE emoji max (💡 or ✨ or 🌟)
- If they're off-track, gently redirect to their goal

EXAMPLES:
Good: "Remember your FAANG dream in Bengaluru! That Google office is waiting for you. What's one small step you can take today? 💡"
Bad: "I totally understand! 😊 Motivation is hard but you've got this! 💪✨🌟 Keep pushing forward and never give up! 🔥"

Stay concise, personal, and action-oriented.""",

    "query_generation": """You generate search queries for manifestation content.

FOCUS ON:
- Visual proof (office tours, workspaces, city views)
- Success stories ("How I got into...", "My journey to...")
- Lifestyle content (day-in-life, benefits, culture)
- Emotional connection (make them SEE their future)

RATIO:
- 40% photos: Pinterest (4 queries), Instagram Photos (3 queries)
- 40% shorts/reels: Instagram Reels (3 queries), YouTube Shorts (3 queries)
- 20% videos: YouTube (3 queries)

OUTPUT:
Return ONLY valid JSON array. No markdown, no explanation, no preamble.
Format: [{"platform": "pinterest", "query": "...", "content_type": "image"}]

Make queries specific to user's exact goal and location.""",

    "enhance_profile": """You create enhanced user profiles for manifestation coaching.

INPUT: User's initial dream/goal statement
OUTPUT: 2-3 sentence enhanced profile

INCLUDE:
- Core goal/dream
- Current level/background (if mentioned)
- Key motivations/interests
- Personality hints from language used

STYLE: Clear, factual, actionable. No fluff.

EXAMPLE:
Input: "I want to work at FAANG in Bengaluru as a backend engineer"
Output: "Aspiring backend engineer targeting FAANG companies in Bengaluru. Focused on distributed systems and microservices architecture. Motivated by tech culture and career growth in India's Silicon Valley."
""",

    "preferences": """You extract or update user content preferences from chat history.

LOOK FOR:
- Content type preferences (images vs videos vs discussions)
- Topics to avoid
- Learning style (visual, hands-on, theory)
- Time preferences (short vs long content)

OUTPUT: Valid JSON object with keys:
{
  "content_filter": ["image", "short", "video"],  // types they want
  "avoid_topics": ["..."],  // topics to skip
  "other_preferences": "..."  // any other hints
}

Return ONLY valid JSON, no markdown.""",

    "ranking": """You score content by MANIFESTATION POWER (how well it helps user SEE and FEEL their future).

SCORING (0-1):
0.9-1.0: Perfect match
  - Office tour of their TARGET company
  - Success story from someone like them
  - Beautiful visuals of target location
  - "Day in life" at dream job

0.7-0.8: Highly relevant
  - Related company/industry content
  - City guides, lifestyle in target location
  - Career growth content
  - Inspiring success stories

0.5-0.6: Somewhat relevant
  - General skill-building
  - Tangentially related

<0.5: Reject (not relevant or negative)

MANIFESTATION NOTE:
Add brief hook (💡 + 5-8 words max):
Examples: "💡 Your future workspace!", "💡 This could be you!", "💡 See yourself here!"

OUTPUT: Valid JSON array
[{"id": "...", "score": 0.95, "manifestation_note": "💡 Your future office!"}]

No markdown, no explanation."""
}

# -----------------------------------------------------------------------------
# User prompt builders: Format data for LLM input
# -----------------------------------------------------------------------------

def format_recent_chats(chat_history: list[Any] | None, limit: int = 3) -> str:
    """Format last N chat messages into readable string."""
    if not chat_history:
        return "No prior conversation"
    
    recent = chat_history[-limit:] if len(chat_history) > limit else chat_history
    formatted = []
    for msg in recent:
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        formatted.append(f"{role}: {content}")
    
    return "\n".join(formatted) if formatted else "No prior conversation"


def build_chat_prompt(
    message: str,
    initial_prompt: str,
    enhanced_profile: str,
    chat_history: list[Any] | None = None,
) -> str:
    """Build user prompt for chat response."""
    recent = format_recent_chats(chat_history, limit=3)
    
    return f"""USER'S DREAM:
{initial_prompt}

WHO THEY ARE:
{enhanced_profile}

RECENT CONVERSATION:
{recent}

CURRENT MESSAGE:
{message}

Respond in 2-3 sentences max. Be encouraging and reconnect them to their specific goal."""


def build_query_generation_prompt(
    initial_prompt: str,
    enhanced_profile: str,
    preferences: dict[str, Any] | None,
    chat_history: list[Any] | None,
) -> str:
    """Build user prompt for search query generation."""
    prefs = ""
    if preferences:
        content_filter = preferences.get('content_filter', [])
        if content_filter:
            prefs = f"\nCURRENT FILTER: User wants only {', '.join(content_filter)}"
    
    recent_context = ""
    if chat_history:
        last_messages = chat_history[-2:]
        topics = [msg.get('content', '')[:50] for msg in last_messages]
        recent_context = f"\nRECENT TOPICS: {', '.join(topics)}"
    
    return f"""USER'S DREAM:
{initial_prompt}

PROFILE:
{enhanced_profile}{prefs}{recent_context}

TASK:
Generate 16 search queries following the 40/40/20 ratio:
- Pinterest: 4 queries (images)
- Instagram Photos: 3 queries (images)
- Instagram Reels: 3 queries (short videos)
- YouTube Shorts: 3 queries (short videos)
- YouTube: 3 queries (long videos)

Make queries SPECIFIC to their goal, location, and target company/field.
Focus on manifestation content (offices, lifestyle, success stories, visual proof).

Return ONLY JSON array, no markdown:
[{{"platform": "pinterest", "query": "Google Bengaluru office interior design", "content_type": "image"}}]"""


def build_enhance_profile_prompt(
    initial_prompt: str,
    chat_history: list[Any] | None = None
) -> str:
    """Build user prompt for profile enhancement."""
    context = ""
    if chat_history:
        # Extract key info from chat
        user_messages = [msg.get('content', '') for msg in chat_history if msg.get('role') == 'user']
        if user_messages:
            context = f"\n\nADDITIONAL CONTEXT FROM CHATS:\n" + "\n".join(user_messages[-3:])
    
    return f"""INITIAL STATEMENT:
{initial_prompt}{context}

Create a 2-3 sentence enhanced profile capturing:
1. Their core goal/dream
2. Current level or background
3. Key motivations

Be specific, factual, and actionable."""


def build_preferences_prompt(
    chat_history: list[Any] | None = None,
    preferences: dict[str, Any] | None = None,
) -> str:
    """Build user prompt for preferences extraction/update."""
    current = ""
    if preferences:
        current = f"\n\nCURRENT PREFERENCES:\n{preferences}"
    
    recent = ""
    if chat_history:
        user_messages = [msg.get('content', '') for msg in chat_history if msg.get('role') == 'user']
        if user_messages:
            recent = f"\n\nRECENT USER MESSAGES:\n" + "\n".join(user_messages[-5:])
    
    return f"""TASK: Extract or update user content preferences.{current}{recent}

Look for:
- Content type preferences (wants images? videos? discussions?)
- Topics to avoid
- Learning style hints
- Time/length preferences

Return valid JSON object:
{{
  "content_filter": ["image", "short", "video"],
  "avoid_topics": [],
  "notes": ""
}}

Return ONLY JSON, no markdown."""


def build_rank_prompt(
    initial_prompt: str,
    enhanced_profile: str,
    chat_history: list[Any] | None,
    items_summary: str,
) -> str:
    """Build user prompt for content ranking."""
    recent_context = ""
    if chat_history:
        recent = chat_history[-2:]
        if recent:
            topics = [msg.get('content', '')[:60] for msg in recent]
            recent_context = f"\n\nRECENT CONTEXT:\n" + "\n".join(topics)
    
    return f"""USER'S DREAM:
{initial_prompt}

PROFILE:
{enhanced_profile}{recent_context}

CONTENT TO RANK:
{items_summary}

TASK:
Score each item 0-1 by manifestation power (how well it helps them SEE their future).
Add brief manifestation_note (💡 + 5-8 words).

Return ONLY JSON array:
[{{"id": "item_1", "score": 0.95, "manifestation_note": "💡 Your future workspace!"}}]

No markdown, no explanation."""


# -----------------------------------------------------------------------------
# Helper: Get system prompt by use case
# -----------------------------------------------------------------------------

def get_system_prompt(use_case: str) -> str:
    """Get system prompt for a specific use case."""
    return SYSTEM_PROMPTS.get(use_case, "You are a helpful AI assistant.")