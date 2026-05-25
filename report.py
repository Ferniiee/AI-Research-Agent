from datetime import datetime

def save_report(topic: str, content: str) -> str:
    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Research Report: {topic}\n\n")
        f.write(content)
    return filename