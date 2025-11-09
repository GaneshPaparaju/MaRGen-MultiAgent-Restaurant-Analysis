from agents.researcher import Researcher
from agents.writer import Writer
from agents.reviewer import Reviewer
import os

DATA_DIR = "data"
OUT_DIR = "outputs"

def main():
    yelp = os.path.join(DATA_DIR, "Hybrid_Yelp_Restaurant_Sales (1).csv")
    menu = os.path.join(DATA_DIR, "Menu_Sales_Data.csv")

    print("🔍 Running Researcher...")
    r = Researcher(yelp, menu, OUT_DIR).run()
    print("Facts:", list(r.facts.keys()))

    print("✍️ Writing draft...")
    draft = Writer(OUT_DIR).draft(r.facts, r.figures)
    print("Draft saved to:", draft.html_path)

    print("🧠 Reviewing...")
    reviewer = Reviewer()
    result = reviewer.review(draft.markdown)
    print("\nFeedback:\n", result.feedback)
    with open(os.path.join(OUT_DIR, "report_final.md"), "w", encoding="utf-8") as f:
        f.write(result.revised)
    print("✅ Final report saved in outputs/report_final.md")

if __name__ == "__main__":
    main()
