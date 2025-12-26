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

from sklearn.preprocessing import MinMaxScaler
import chromadb


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
        Initialize the aggregator and establish a connection
        to the ChromaDB collection.
        """
        self.N = None
        self.k = None
        self.pn = None
        self.chroma_collection = None
        self.init_connection()

    # -------------------------------------------------------------------
    # Configuration
    # -------------------------------------------------------------------
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
                chroma_client = chromadb.PersistentClient(path="../data/chroma")
                self.chroma_collection = chroma_client.get_or_create_collection(
                    name="articles_with_score"
                )
                return
            except Exception as e:
                retries += 1
                print(e)

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
        max_retries = 5
        retries = 0

        while retries < max_retries:
            try:
                return self.chroma_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=max_similarities
                )
            except Exception as e:
                retries += 1
                print(e)

        raise RuntimeError("Failed to query ChromaDB after multiple attempts")

    # -------------------------------------------------------------------
    # Page distribution
    # -------------------------------------------------------------------
    def distribution_function(self, number_of_pages):
        """
        Compute an exponential probability distribution over result pages.
        Function: p(x) = e^-x

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
        values_to_scale = np.array([
            collection_dict["year"],
            collection_dict["n_citation"],
            collection_dict["gov_score"]
        ]).T

        scaler = MinMaxScaler()
        scaled_values = scaler.fit_transform(values_to_scale)

        collection_dict["year_normalized"] = scaled_values[:, 0].tolist()
        collection_dict["citations_normalized"] = scaled_values[:, 1].tolist()
        collection_dict["points_normalized"] = scaled_values[:, 2].tolist()

        collection_dict["score"] = [
            self.pn[0] * collection_dict["similarity"][i] +
            self.pn[1] * collection_dict["year_normalized"][i] +
            self.pn[2] * collection_dict["citations_normalized"][i] +
            self.pn[3] * collection_dict["points_normalized"][i]
            for i in range(len(collection_dict["id"]))
        ]

        ranked = sorted(
            [
                {
                    "id": collection_dict["id"][i],
                    "title": collection_dict["title"][i],
                    "similarity": collection_dict["similarity"][i],
                    "year": collection_dict["year"][i],
                    "n_citation": collection_dict["n_citation"][i],
                    "gov_score": collection_dict["gov_score"][i],
                    "score": collection_dict["score"][i],
                }
                for i in range(len(collection_dict["id"]))
            ],
            key=lambda x: x["score"],
            reverse=True
        )

        ranked_ids = [entry["id"] for entry in ranked]
        pages = [
            ranked_ids[i:i + self.N]
            for i in range(0, len(ranked_ids), self.N)
        ]

        page_distribution = self.distribution_function(len(pages))
        selected_papers = []

        last_page_count = len(pages)
        active_pages = pages

        for iteration in range(self.k):
            if self.k > self.N and iteration >= self.N:
                active_pages = [page for page in pages if page]
                if len(active_pages) != last_page_count:
                    page_distribution = self.distribution_function(len(active_pages))
                    last_page_count = len(active_pages)

            page_idx = np.random.choice(len(active_pages), p=page_distribution)
            page = active_pages[page_idx]
            paper_id = np.random.choice(page)

            selected_papers.append(paper_id)
            pages[page_idx] = [pid for pid in page if pid != paper_id]

        return collections.Counter(selected_papers)
