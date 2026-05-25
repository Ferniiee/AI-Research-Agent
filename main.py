import sys, os
from agent import run
from datetime import datetime

def save_report(topic: str, content: str):
    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Research Report: {topic}\n\n")
        f.write(content)
    print(f"\n Report saved to {filename}")
    return filename

if __name__ == "__main__":
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Research topic: ")
    report = run(topic)
    print("\n" + "="*60)
    print(report[:500] + "...")
    save_report(topic, report)
