from app.models.chat import Query


# Generates queries in ratio: 40% photos, 40% shorts/reels, 20% videos (placeholder counts).
def generate_queries_ratio(user_goal: str) -> list[Query]:
    goal = (user_goal or "career growth").strip()
    queries: list[Query] = []
    for i in range(4):
        queries.append(Query(platform="pinterest", query=goal, content_type="image"))
    for i in range(3):
        queries.append(Query(platform="instagram", query=goal, content_type="image"))
    for i in range(3):
        queries.append(Query(platform="instagram", query=goal, content_type="short"))
    for i in range(3):
        queries.append(Query(platform="youtube", query=goal, content_type="short"))
    for i in range(3):
        queries.append(Query(platform="youtube", query=goal, content_type="video"))
    return queries
