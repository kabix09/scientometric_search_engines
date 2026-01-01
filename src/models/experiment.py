# -*- coding: utf-8 -*-

"""
Experiment orchestration module.

Defines the Experiment class responsible for coordinating
large-scale simulation runs. It integrates the simulation engine
(VirtualAggregator) with batching, checkpointing, and result persistence.
"""

import os
import csv
import gc
import logging
import pandas as pd
import numpy as np
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
        Load precomputed query embeddings.
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
        # Resume progress based on the first configuration
        already_saved = int(progress_status.get(0, {}).get("controll_sum", 0) or 0)

        logger.info(f"Skipping already processed queries: {already_saved}")

        distribution_dict = {}
        result_buffer = {}
        processed = 0

        start_index = already_saved
        end_index = min(start_index + batch, len(self.queries))

        logger.info(f"Processing query range: {start_index}–{end_index}")

        for query_offset, query_embedding in enumerate(
            tqdm(self.queries[start_index:end_index], desc="Queries")
        ):
            # Ensure deterministic randomness across batches
            global_query_id = start_index + query_offset
            np.random.seed(hash(str(42 + global_query_id)) % (2**32 - 1))

            # Retrieve top-N similar articles (single I/O-heavy operation per query)
            self.similar_articles = self.virtual_aggregator.get_similar_articles(
                query_embedding,
                max_similarities=250
            )

            # Preprocess candidate features once per query
            prepared_candidates = self.virtual_aggregator.prepare_candidates(
                self.similar_articles
            )

            # Iterate over all parameter configurations
            for settings_id, config in enumerate(self.settings):
                self.virtual_aggregator.set_parameters(
                    config["N"],
                    config["k"],
                    config["pn"]
                )

                step_distribution = self.step(prepared_candidates)

                # Buffer per-query results
                if settings_id not in result_buffer:
                    result_buffer[settings_id] = {
                        "query_id": [global_query_id],
                        "distribution": [dict(step_distribution)]
                    }
                else:
                    result_buffer[settings_id]["query_id"].append(global_query_id)
                    result_buffer[settings_id]["distribution"].append(
                        dict(step_distribution)
                    )

                # Aggregate global distributions
                settings_key = str(config)
                if settings_key in distribution_dict:
                    distribution_dict[settings_key].update(step_distribution)
                else:
                    distribution_dict[settings_key] = step_distribution

            processed += 1

            # Periodic checkpointing
            if processed % 2500 == 0:
                self.save_distribution(distribution_dict)
                self.save_results(result_buffer)
                result_buffer = {}

        logger.info("Final result persistence")
        self.save_distribution(distribution_dict)
        self.save_results(result_buffer)

    # -------------------------------------------------------------------
    # Single simulation step
    # -------------------------------------------------------------------
    def step(self, prepared_candidates):
        """
        Execute a single aggregation step using preprocessed candidates.

        Returns:
            collections.Counter: Sampled paper distribution.
        """
        return self.virtual_aggregator.rank_and_sample(prepared_candidates)

    # -------------------------------------------------------------------
    # Persistence
    # -------------------------------------------------------------------
    def save_results(self, result_dict):
        """
        Save per-configuration simulation results to CSV files.
        """
        for settings_id, data in result_dict.items():
            if not data["query_id"]:
                continue
            
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
        Save aggregated global distributions across all configurations.
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

    # -------------------------------------------------------------------
    # Atomic execution (testing / notebooks)
    # -------------------------------------------------------------------
    def run_single_query(self, query_id_or_embedding, seed=42):
        """
        Execute the simulation for a single query across all configurations.
        Results are returned in memory and not persisted.

        Args:
            query_id_or_embedding (int or list): Query index or raw embedding.
            seed (int): Random seed for reproducibility.

        Returns:
            dict: Mapping of settings_id to distribution counters.
        """
        if isinstance(query_id_or_embedding, int):
            if self.queries is None:
                self.load_queries()
            query_embedding = self.queries[query_id_or_embedding]
        else:
            query_embedding = query_id_or_embedding

        np.random.seed(seed)

        raw_results = self.virtual_aggregator.get_similar_articles(
            query_embedding,
            max_similarities=250
        )

        prepared_candidates = self.virtual_aggregator.prepare_candidates(raw_results)

        test_results = {}
        for settings_id, config in enumerate(self.settings):
            self.virtual_aggregator.set_parameters(
                config["N"],
                config["k"],
                config["pn"]
            )
            test_results[settings_id] = self.step(prepared_candidates)

        return test_results
