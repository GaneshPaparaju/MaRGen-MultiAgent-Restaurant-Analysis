import pandas as pd
import os
from dataclasses import dataclass

@dataclass
class RetrieverOutput:
    dataframe: pd.DataFrame
    restaurant_name: str | None = None

class Retriever:
    """
    Retriever Agent for MaRGen system.
    Reads data sources and filters relevant records based on user query.
    """

    def __init__(self, yelp_path: str, menu_path: str):
        self.yelp_path = yelp_path
        self.menu_path = menu_path
        print("🔎 Retriever Agent initialized")

    # --------------------------------------------------------------
    def query(self, query_text: str) -> pd.DataFrame:
        """Load data, detect restaurant mention, and join sources."""
        yelp_df = pd.read_csv(self.yelp_path)
        menu_df = pd.read_csv(self.menu_path)

        # Normalize column names
        yelp_df.columns = [c.lower().strip() for c in yelp_df.columns]
        menu_df.columns = [c.lower().strip() for c in menu_df.columns]

        # Try to detect a restaurant name in the query
        restaurant_name = None
        if "restaurant_name" in yelp_df.columns:
            for name in yelp_df["restaurant_name"].dropna().unique():
                if name.lower() in query_text.lower():
                    restaurant_name = name
                    break

        # Apply restaurant filter if detected
        if restaurant_name:
            print(f"🎯 Filtering records for restaurant: {restaurant_name}")
            yelp_df = yelp_df[yelp_df["restaurant_name"].str.lower() == restaurant_name.lower()]
            menu_df = menu_df[menu_df["restaurant_name"].str.lower() == restaurant_name.lower()] \
                if "restaurant_name" in menu_df.columns else menu_df

        # Join data
        join_key = "restaurant_id" if "restaurant_id" in yelp_df.columns else None
        if join_key and join_key in menu_df.columns:
            merged = menu_df.merge(yelp_df, on=join_key, how="left")
        else:
            # fallback join by restaurant name
            merged = menu_df.merge(
                yelp_df,
                left_on="restaurant_name" if "restaurant_name" in menu_df.columns else None,
                right_on="restaurant_name" if "restaurant_name" in yelp_df.columns else None,
                how="left",
            )

        merged["restaurant_name_detected"] = restaurant_name
        print(f"✅ Retrieved {len(merged)} records (restaurant filter: {restaurant_name or 'None'})")

        return merged
