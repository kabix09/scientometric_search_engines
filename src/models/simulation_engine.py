# -*- coding: utf-8 -*-

"""
Simulation-based aggregation engine.

This module defines the VirtualAggregator class, which simulates the
selection of scientific publications based on multiple weighted criteria:
- semantic similarity
- publication year
- citation count
- official government score

The class operates on a persistent ChromaDB collection and produces
a probabilistic distribution of selected papers.
"""

import collections
import numpy as np
import pandas as pd
import joblib  # Added for loading the global scaler
import chromadb
import random

# -------------------------------------------------------------------
# Virtual aggregation engine
# -------------------------------------------------------------------
class VirtualAggregator:
    """
    Simulation engine for probabilistic paper selection.

    The engine retrieves semantically similar documents from a vector
    database, ranks them using a weighted scoring function, paginates
    the ranking, and samples papers according to an exponential
    page-based probability distribution.
    """

    def __init__(self):
        """
        Initialize the aggregator and load the PRE-FITTED global scaler.
        """
        self.N = None
        self.k = None
        self.pn = None
        self.chroma_collection = None
        
        # Load global scaler instead of local fitting
        # Ensure you have generated this file using prepare_global_scaler.py
        try:
            self.scaler = joblib.load('models/global_scaler.pkl')
        except FileNotFoundError:
            raise RuntimeError("Global scaler not found at models/global_scaler.pkl. Run preparation script first.")
            
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

        Retries the connection several times before failing.
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
            dict: ChromaDB query response.
        """
        return self.chroma_collection.query(
            query_embeddings=[query_embedding],
            n_results=max_similarities
        )

    # -------------------------------------------------------------------
    # Page distribution
    # -------------------------------------------------------------------
    def distribution_function(self, number_of_pages):
        """
        Compute an exponential probability distribution over result pages.
        Function: p(x) = e^-x (distribution for page selection.)

        Args:
            number_of_pages (int): Number of ranked pages.

        Returns:
            np.ndarray: Normalized probability distribution.
        """
        distribution = np.exp(-np.arange(1, number_of_pages + 1))
        distribution /= distribution.sum()
        return distribution

    # -------------------------------------------------------------------
    # Ranking and sampling
    # -------------------------------------------------------------------
    def distribution_generator(self, collection_dict):
        """
        Rank retrieved articles and sample papers probabilistically.

        The ranking score is computed as a weighted sum of normalized
        features and semantic similarity.

        Args:
            collection_dict (dict): Dictionary containing article attributes:
                id, title, similarity, year, n_citation, gov_score

        Returns:
            collections.Counter: Selected paper identifiers with frequencies.
        """

        # 1. Feature preparation with Log Scaling (Solution 2)
        citations_raw = np.array(collection_dict["n_citation"])
        citations_log = np.log1p(citations_raw)

        # 2. Apply GLOBAL Scaling (Solution 1)
        # We use .transform() instead of .fit_transform() to maintain consistency across batches
        values_to_scale = np.array([
            collection_dict["year"],
            citations_log,
            collection_dict["gov_score"]
        ]).T
        
        scaled_values = self.scaler.transform(values_to_scale)

        # 3. Distance to Similarity transformation (Point A)
        distances = np.array(collection_dict["distance"])

        # Konwersja na podobieństwo: 1.0 - dystans (z progiem bezpieczeństwa 0.0)
        similarities = np.maximum(0, 1 - distances)

        # 4. Final weighted score calculation
        # pn[0]*sim + pn[1]*year + pn[2]*citations + pn[3]*gov
        scores = (
            self.pn[0] * similarities +
            self.pn[1] * scaled_values[:, 0] +
            self.pn[2] * scaled_values[:, 1] +
            self.pn[3] * scaled_values[:, 2]
        )

        # 5. Sorting and Pagination
        sorted_indices = np.argsort(-scores)
        ranked_ids = [str(x) for x in np.array(collection_dict["id"])[sorted_indices]]

        pages = [
            ranked_ids[i:i + self.N] 
            for i in range(0, len(ranked_ids), self.N)
        ]

        # 6. Sampling (Fixed logic - sampling without replacement)
        selected_papers = []
        # working_pages ensures we don't modify the source structure accidentally
        working_pages = [list(p) for p in pages]

        for _ in range(self.k):
            active_indices = [idx for idx, p in enumerate(working_pages) if len(p) > 0]
            
            if not active_indices:
                break

            # Re-calculate distribution based on the current number of non-empty pages
            page_distribution = self.distribution_function(len(active_indices))

            # Select relative index from the list of active pages
            rel_idx = np.random.choice(len(active_indices), p=page_distribution)
            # Map relative index back to the absolute page index
            abs_page_idx = active_indices[rel_idx]
            
            # Select and remove the paper from the specific page
            page = working_pages[abs_page_idx]
            paper_id = random.choice(page)

            selected_papers.append(paper_id)
            
            # Remove the selected paper from the page to allow sampling without replacement
            working_pages[abs_page_idx].remove(paper_id)

        return collections.Counter(selected_papers)
