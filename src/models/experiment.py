# -*- coding: utf-8 -*-

"""
Experiment orchestration module.

This module defines the Experiment class, responsible for coordinating
large-scale simulation runs. It connects the simulation engine
(VirtualAggregator) with batch processing, checkpointing, and result
persistence.
"""

import os
import csv
import gc
import logging
import pandas as pd
from tqdm import tqdm

try:
    from src.models.simulation_engine import VirtualAggregator
except ImportError:
    from simulation_engine import VirtualAggregator


# -------------------------------------------------------------------
# Logging configuration
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# -------------------------------------------------------------------
# Experiment orchestrator
# -------------------------------------------------------------------
class Experiment:
    """
    Orchestrates simulation experiments over a large set of queries
    and parameter configurations.
    """

    def __init__(self, settings):
        """
        Initialize the experiment.

        Args:
            settings (list[dict]): List of simulation parameter configurations.
        """
        self.virtual_aggregator = VirtualAggregator()
        self.settings = settings
        self.queries = None
        self.similar_articles = None

    # -------------------------------------------------------------------
    # Data loading
    # -------------------------------------------------------------------
    def load_queries(self):
        """
        Load precomputed query embeddings from the interim directory.
        """
        path = "data/interim/queries_with_embeddings.pkl"
        logger.info(f"Loading queries from {path}")

        df_queries = pd.read_pickle(path)[["embedding"]]
        self.queries = df_queries["embedding"].tolist()

        del df_queries
        gc.collect()

    # -------------------------------------------------------------------
    # Experiment execution
    # -------------------------------------------------------------------
    def run_experiment(self, batch=40_000):
        """
        Run the experiment for a batch of queries.

        Args:
            batch (int): Number of queries processed in a single run.
        """
        logger.info("Starting experiment execution")
        self.load_queries()

        progress_status = self.health_check()
        already_saved = int(progress_status.get(0, {}).get("controll_sum", 0) or 0)

        logger.info(f"Skipping already processed queries: {already_saved}")

        distribution_dict = {}
        result_buffer = {}
        processed = 0

        start_index = already_saved
        end_index = start_index + batch

        logger.info(f"Processing query range: {start_index}–{end_index}")

        for query_offset, query_embedding in enumerate(
            tqdm(self.queries[start_index:end_index], desc="Queries")
        ):
            self.similar_articles = self.virtual_aggregator.get_similar_articles(
                query_embedding,
                max_similarities=250
            )

            for settings_id, config in enumerate(self.settings):
                self.virtual_aggregator.set_parameters(
                    config["N"],
                    config["k"],
                    config["pn"]
                )

                step_distribution = self.step()

                if settings_id not in result_buffer:
                    result_buffer[settings_id] = {
                        "query_id": [start_index + query_offset],
                        "distribution": [dict(step_distribution)]
                    }
                else:
                    result_buffer[settings_id]["query_id"].append(
                        start_index + query_offset
                    )
                    result_buffer[settings_id]["distribution"].append(
                        dict(step_distribution)
                    )

                settings_key = str(config)
                if settings_key in distribution_dict:
                    distribution_dict[settings_key].update(step_distribution)
                else:
                    distribution_dict[settings_key] = step_distribution

            processed += 1

            if processed % 500 == 0:
                self.save_distribution(distribution_dict)
                self.save_results(result_buffer)
                result_buffer = {}

        logger.info("Final result persistence")
        self.save_distribution(distribution_dict)
        self.save_results(result_buffer)

    # -------------------------------------------------------------------
    # Single simulation step
    # -------------------------------------------------------------------
    def step(self):
        """
        Prepare data and execute a single aggregation step.

        Returns:
            collections.Counter: Sampled paper distribution.
        """
        collection_dict = {
            "id": self.similar_articles["ids"][0],
            "title": self.similar_articles["documents"][0],
            "similarity": self.similar_articles["distances"][0],
            "year": [
                metadata["year"]
                for metadata in self.similar_articles["metadatas"][0]
            ],
            "n_citation": [
                metadata["n_citation"]
                for metadata in self.similar_articles["metadatas"][0]
            ],
            "gov_score": [
                metadata["gov_score"]
                for metadata in self.similar_articles["metadatas"][0]
            ],
        }

        return self.virtual_aggregator.distribution_generator(collection_dict)

    # -------------------------------------------------------------------
    # Persistence
    # -------------------------------------------------------------------
    def save_results(self, result_dict):
        """
        Save per-configuration simulation results to CSV files.
        """
        for settings_id, data in result_dict.items():
            directory = f"data/results/{settings_id}"
            os.makedirs(directory, exist_ok=True)

            file_path = f"{directory}/results.csv"
            file_exists = os.path.isfile(file_path)

            with open(file_path, "a", newline="") as csvfile:
                writer = csv.DictWriter(
                    csvfile,
                    fieldnames=["query_id", "distribution"]
                )

                if not file_exists:
                    writer.writeheader()

                for i in range(len(data["query_id"])):
                    writer.writerow({
                        "query_id": data["query_id"][i],
                        "distribution": data["distribution"][i],
                    })

    def save_distribution(self, distribution_dict):
        """
        Save aggregated global distributions across configurations.
        """
        df = pd.DataFrame(
            list(distribution_dict.items()),
            columns=["settings", "distribution"]
        )
        df["distribution"] = df["distribution"].apply(dict)
        df.to_csv(
            "data/processed/global_distributions.csv",
            index=False
        )

    # -------------------------------------------------------------------
    # Progress recovery
    # -------------------------------------------------------------------
    def health_check(self):
        """
        Check how many queries have already been processed per configuration.

        Returns:
            dict: Mapping of configuration index to processed record count.
        """
        base_path = "data/results"
        results = {}

        if not os.path.exists(base_path):
            return results

        for idx in range(len(self.settings)):
            file_path = os.path.join(base_path, str(idx), "results.csv")
            try:
                with open(file_path, "r") as file:
                    line_count = sum(1 for _ in file) - 1
                    results[idx] = {"controll_sum": max(0, line_count)}
            except FileNotFoundError:
                results[idx] = {"controll_sum": 0}

        return results
