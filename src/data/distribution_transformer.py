# -*- coding: utf-8 -*-

import pandas as pd
import json
import os
from collections import Counter
from tqdm import tqdm


class DistributionTransformer:
    def __init__(self, metadata_path="data/interim/articles_with_score_df.csv"):
        """
        Initialize the transformer and load article metadata.

        Builds a fast lookup dictionary mapping:
        article_id (str) -> citation count (int)
        """
        print("Loading metadata for distribution transformation...")
        df_meta = pd.read_csv(metadata_path)

        # Fast lookup dictionary: article_id -> number of citations
        # self.id_to_citation = pd.Series(
        #     df_meta.n_citation.values,
        #     index=df_meta.id.astype(str)
        # ).to_dict()

        self.id_to_citation = {
            str(idx + 1): row["n_citation"] 
            for idx, row in df_meta.iterrows()
        }

    def transform_to_citations(
        self,
        input_path="data/processed/global_distributions.csv",
        output_path="data/processed/final_citation_distributions.csv"
    ):
        """
        Transform article-level selection distributions into citation-level distributions.

        Each article ID in the global distribution is replaced by its citation count.
        The output represents a density distribution over citation values
        for each experimental configuration.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        print(f"Starting transformation of results from {input_path}...")
        df_results = pd.read_csv(input_path)

        final_rows = []

        for _, row in tqdm(
            df_results.iterrows(),
            total=len(df_results),
            desc="Transforming distributions"
        ):
            # 1. Load distribution dictionary (robust JSON parsing)
            try:
                # Normalize quotes to ensure valid JSON format
                dist_dict = json.loads(row["distribution"].replace("'", '"'))
            except Exception:
                # Fallback for Python literal dictionaries
                import ast
                dist_dict = ast.literal_eval(row["distribution"])

            # 2. Aggregate selections by citation count
            # Result: Counter({citation_count: total_selections})
            citation_counter = Counter()
            for paper_id, selection_count in dist_dict.items():
                n_cit = self.id_to_citation.get(str(paper_id))
                if n_cit is not None:
                    citation_counter[n_cit] += selection_count

            # 3. Store transformed result
            final_rows.append({
                "settings": row["settings"],
                "citation_distribution": dict(citation_counter)
            })

        # Persist transformed distributions
        df_final = pd.DataFrame(final_rows)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df_final.to_csv(output_path, index=False)

        print(f"Transformation completed successfully. Output saved to: {output_path}")
