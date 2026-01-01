# -*- coding: utf-8 -*-

"""
Simulation-based aggregation engine.

This module defines the VirtualAggregator class, which simulates
the selection of scientific publications based on multiple weighted criteria:
- semantic similarity
- publication year
- citation count
- official government score

The engine operates on a persistent ChromaDB collection and produces
a probabilistic distribution of selected papers.
"""

import collections
import numpy as np
import pandas as pd
import joblib
import chromadb
import random


# -------------------------------------------------------------------
# Virtual aggregation engine
# -------------------------------------------------------------------
class VirtualAggregator:
    """
    Simulation engine for probabilistic paper selection.

    The engine retrieves semantically similar documents from a vector
    database, computes weighted relevance scores, paginates ranked results,
    and samples papers according to an exponential page-based probability
    distribution.
    """

    def __init__(self):
        """
        Initialize the aggregator and load the pre-fitted global scaler.
        """
        self.N = None
        self.k = None
        self.pn = None
        self.chroma_collection = None

        # Load globally fitted scaler to ensure consistency across experiments
        try:
            self.scaler = joblib.load("models/global_scaler.pkl")
        except FileNotFoundError:
            raise RuntimeError(
                "Global scaler not found at models/global_scaler.pkl. "
                "Run the scaler preparation step first."
            )

        self.init_connection()

    def set_parameters(self, N, k, pn):
        """
        Set simulation parameters.

        Args:
            N (int): Page size (number of papers per page).
            k (int): Number of papers to sample.
            pn (list[float]): Criterion weights in the following order:
                [similarity, year, citation count, government score]
        """
        self.N = N
        self.k = k
        self.pn = pn

    # -------------------------------------------------------------------
    # Database connection
    # -------------------------------------------------------------------
    def init_connection(self):
        """
        Initialize a persistent connection to the ChromaDB collection.

        The method retries the connection multiple times before failing.
        """
        max_retries = 5
        retries = 0

        while retries < max_retries:
            try:
                chroma_client = chromadb.PersistentClient(path="data/chroma")
                self.chroma_collection = chroma_client.get_or_create_collection(
                    name="articles_with_score"
                )
                return
            except Exception as e:
                retries += 1
                print(f"Retry {retries}/{max_retries} - Error: {e}")

        raise RuntimeError("Failed to connect to ChromaDB after multiple attempts")

    # -------------------------------------------------------------------
    # Vector search
    # -------------------------------------------------------------------
    def get_similar_articles(self, query_embedding, max_similarities):
        """
        Retrieve semantically similar articles from ChromaDB.

        Args:
            query_embedding (list or np.ndarray): Query embedding vector.
            max_similarities (int): Number of results to retrieve.

        Returns:
            dict: Raw ChromaDB query response.
        """
        return self.chroma_collection.query(
            query_embeddings=[query_embedding],
            n_results=max_similarities
        )

    # -------------------------------------------------------------------
    # Page probability distribution
    # -------------------------------------------------------------------
    def distribution_function(self, number_of_pages):
        """
        Compute an exponential probability distribution over ranked pages.

        The probability of selecting page x is proportional to exp(-x).

        Args:
            number_of_pages (int): Number of ranked pages.

        Returns:
            np.ndarray: Normalized probability distribution.
        """
        distribution = np.exp(-np.arange(1, number_of_pages + 1))
        distribution /= distribution.sum()
        return distribution

    # -------------------------------------------------------------------
    # Candidate preparation
    # -------------------------------------------------------------------
    def prepare_candidates(self, results):
        """
        Preprocess candidate articles once per query.

        This method performs similarity transformation, log-scaling of
        citation counts, and global normalization of numeric features.

        Args:
            results (dict): Raw ChromaDB query response.

        Returns:
            dict: Preprocessed candidate features ready for scoring.
        """
        ids = [str(x) for x in results["ids"][0]]

        # Convert distances to similarity scores
        distances = np.array(results["distances"][0])
        similarities = np.maximum(0, 1 - distances)

        # Extract metadata
        years = [m["year"] for m in results["metadatas"][0]]
        citations = [m["n_citation"] for m in results["metadatas"][0]]
        gov_scores = [m["gov_score"] for m in results["metadatas"][0]]

        # Log-transform citation counts
        citations_log = np.log1p(np.array(citations))

        # Apply global normalization
        features = np.column_stack([years, citations_log, gov_scores])
        scaled_features = self.scaler.transform(features)

        return {
            "ids": ids,
            "sim": similarities,
            "scaled": scaled_features
        }

    # -------------------------------------------------------------------
    # Ranking and sampling
    # -------------------------------------------------------------------
    def rank_and_sample(self, candidates):
        """
        Rank candidate articles and sample papers probabilistically.

        Args:
            candidates (dict): Output of prepare_candidates().

        Returns:
            collections.Counter: Sampled paper identifiers with frequencies.
        """
        scores = (
            self.pn[0] * candidates["sim"] +
            self.pn[1] * candidates["scaled"][:, 0] +
            self.pn[2] * candidates["scaled"][:, 1] +
            self.pn[3] * candidates["scaled"][:, 2]
        )

        sorted_indices = np.argsort(-scores)
        ranked_ids = [candidates["ids"][i] for i in sorted_indices]

        pages = [
            ranked_ids[i:i + self.N]
            for i in range(0, len(ranked_ids), self.N)
        ]

        selected_papers = []
        working_pages = [list(p) for p in pages]

        for _ in range(self.k):
            active_indices = [
                idx for idx, p in enumerate(working_pages) if len(p) > 0
            ]
            if not active_indices:
                break

            page_distribution = self.distribution_function(len(active_indices))
            rel_idx = np.random.choice(len(active_indices), p=page_distribution)
            abs_page_idx = active_indices[rel_idx]

            page = working_pages[abs_page_idx]
            paper_id = random.choice(page)

            selected_papers.append(paper_id)
            working_pages[abs_page_idx].remove(paper_id)

        return collections.Counter(selected_papers)

    # -------------------------------------------------------------------
    # Legacy compatibility
    # -------------------------------------------------------------------
    def distribution_generator(self, collection_dict):
        """
        Legacy wrapper for backward compatibility with older interfaces.
        """
        mock_results = {
            "ids": [collection_dict["id"]],
            "distances": [collection_dict["distance"]],
            "metadatas": [[
                {"year": y, "n_citation": c, "gov_score": g}
                for y, c, g in zip(
                    collection_dict["year"],
                    collection_dict["n_citation"],
                    collection_dict["gov_score"]
                )
            ]]
        }
        prepared = self.prepare_candidates(mock_results)
        return self.rank_and_sample(prepared)
