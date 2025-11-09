import os
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ResearchOutput:
    facts: Dict
    figures: List[str]

class Researcher:
    """
    Researcher Agent – analyzes data and creates visual insights
    """

    def __init__(self, yelp_path: str, menu_path: str, restaurant_filter: Optional[str] = None):
        self.yelp_path = yelp_path
        self.menu_path = menu_path
        self.restaurant_filter = restaurant_filter
        self.yelp = pd.read_csv(yelp_path)
        self.menu = pd.read_csv(menu_path)
        self.facts: Dict = {}
        self.figures: List[str] = []
        os.makedirs("outputs", exist_ok=True)
        print("🔬 Researcher Agent initialized")

    # ------------------------------------------------------------------
    def run(self) -> ResearchOutput:
        """Main analysis pipeline"""
        try:
            # ------------------------------------------------------------
            # 1️⃣ General Revenue Stats
            if "revenue" in self.menu.columns:
                total_rev = self.menu["revenue"].sum()
                avg_rev = self.menu["revenue"].mean()
                self.facts["total_revenue"] = float(total_rev)
                self.facts["avg_revenue"] = float(avg_rev)

            self.facts["total_records"] = len(self.menu)
            if "item_name" in self.menu.columns:
                self.facts["unique_items"] = self.menu["item_name"].nunique()

            # ------------------------------------------------------------
            # 2️⃣ Top Categories and Items
            if "category" in self.menu.columns and "revenue" in self.menu.columns:
                top_cat = self.menu.groupby("category")["revenue"].sum().sort_values(ascending=False)
                self.facts["top_category"] = top_cat.index[0]
                self.facts["top_category_revenue"] = float(top_cat.iloc[0])

                fig_path = os.path.join("outputs", "top_categories_revenue.png")
                plt.figure(figsize=(8,4))
                top_cat.head(10).plot(kind="bar", title="Top Categories by Revenue")
                plt.tight_layout(); plt.savefig(fig_path); plt.close()
                self.figures.append(fig_path)

            if "item_name" in self.menu.columns and "revenue" in self.menu.columns:
                top_items = self.menu.groupby("item_name")["revenue"].sum().sort_values(ascending=False).head(10)
                fig_path = os.path.join("outputs", "top_items_revenue.png")
                plt.figure(figsize=(8,4))
                top_items.plot(kind="bar", color="orange", title="Top Menu Items by Revenue")
                plt.tight_layout(); plt.savefig(fig_path); plt.close()
                self.figures.append(fig_path)

            # ------------------------------------------------------------
            # 3️⃣ Monthly Trend (if date present)
            if "date" in self.menu.columns:
                self.menu["date"] = pd.to_datetime(self.menu["date"], errors="coerce")
                monthly_rev = self.menu.groupby(self.menu["date"].dt.to_period("M"))["revenue"].sum()
                fig_path = os.path.join("outputs", "monthly_trend.png")
                plt.figure(figsize=(8,4))
                monthly_rev.plot(kind="line", marker="o", title="Monthly Revenue Trend")
                plt.tight_layout(); plt.savefig(fig_path); plt.close()
                self.figures.append(fig_path)
                self.facts["start_date"] = str(self.menu["date"].min().date())
                self.facts["end_date"] = str(self.menu["date"].max().date())

            # ------------------------------------------------------------
            # 4️⃣ Sales Optimization Add-on (NEW)
            try:
                # Promotion Effect
                if "promotion" in self.menu.columns and "revenue" in self.menu.columns:
                    promo_eff = (
                        self.menu.groupby("promotion")["revenue"]
                        .mean().rename({0: "No Promo", 1: "Promo"})
                        .to_dict()
                    )
                    self.facts["promotion_effect"] = promo_eff

                # Weather Impact
                weather_col = next((c for c in self.yelp.columns if "weather" in c.lower()), None)
                if weather_col and "revenue" in self.yelp.columns:
                    weather_impact = self.yelp.groupby(weather_col)["revenue"].mean().to_dict()
                    self.facts["weather_impact"] = weather_impact

                # Cuisine Performance
                if "category" in self.menu.columns:
                    top_cuis = (
                        self.menu.groupby("category")["revenue"]
                        .sum().sort_values(ascending=False).head(5)
                    )
                    self.facts["top_cuisines"] = top_cuis.to_dict()
            except Exception as e:
                print(f"⚠ Sales optimization analysis skipped: {e}")

            # ------------------------------------------------------------
            print("✅ Research analysis complete")
            return ResearchOutput(facts=self.facts, figures=self.figures)

        except Exception as e:
            print(f"❌ Researcher error: {e}")
            return ResearchOutput(facts={"error": str(e)}, figures=[])
