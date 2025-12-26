# -*- coding: utf-8 -*-

"""
Feature construction and vector database preparation script.

This module:
1. Generates sentence embeddings for article titles.
2. Stores embeddings in an intermediate pickle file.
3. Loads embeddings into a persistent ChromaDB collection.
4. Generates synthetic search queries and their embeddings.

The produced artifacts are intended to be reused across experiments
to avoid repeated embedding computation.
"""

import os
import random
import logging
import pandas as pd
import torch
import chromadb
from tqdm import tqdm
from sentence_transformers import SentenceTransformer


# -------------------------------------------------------------------
# Logging configuration
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# -------------------------------------------------------------------
# Feature and embedding builder
# -------------------------------------------------------------------
class FeatureBuilder:
    """
    Responsible for text feature generation and embedding persistence.

    This class encapsulates:
    - SentenceTransformer initialization
    - Article title embedding generation
    - Query generation and embedding
    - Vector database ingestion
    """

    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """
        Initialize the SentenceTransformer model.

        Args:
            model_name (str): Name of the pretrained SentenceTransformer model.
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Initializing model '{model_name}' on device: {self.device}")
        self.model = SentenceTransformer(model_name, device=self.device)

    # -------------------------------------------------------------------
    # Article embeddings
    # -------------------------------------------------------------------
    def create_article_embeddings(self, input_path, output_path, batch_size=128):
        """
        Generate embeddings for article titles and persist them to disk.

        Args:
            input_path (str): CSV file containing article metadata.
            output_path (str): Output pickle file path.
            batch_size (int): Encoding batch size.

        Returns:
            pd.DataFrame: DataFrame with embedded titles.
        """
        logger.info(f"Loading articles from {input_path}")
        df = pd.read_csv(input_path)

        titles = df["title"].tolist()
        logger.info(f"Encoding {len(titles)} article titles (batch_size={batch_size})")

        embeddings = self.model.encode(
            titles,
            batch_size=batch_size,
            show_progress_bar=True
        )

        df["embedding"] = list(embeddings)
        df.to_pickle(output_path)

        logger.info(f"Article embeddings saved to {output_path}")
        return df

    # -------------------------------------------------------------------
    # Vector database ingestion
    # -------------------------------------------------------------------
    def load_to_chroma(
        self,
        df_path,
        chroma_path,
        collection_name="articles_with_score",
        batch_size=5000
    ):
        """
        Load embedded articles into a persistent ChromaDB collection.

        Args:
            df_path (str): Pickle file containing embeddings.
            chroma_path (str): Directory for ChromaDB persistence.
            collection_name (str): ChromaDB collection name.
            batch_size (int): Upload batch size.
        """
        logger.info(f"Initializing ChromaDB at {chroma_path}")
        df = pd.read_pickle(df_path)

        client = chromadb.PersistentClient(path=chroma_path)
        collection = client.get_or_create_collection(name=collection_name)

        logger.info(f"Uploading {len(df)} records to ChromaDB")

        for i in tqdm(range(0, len(df), batch_size), desc="Chroma Upload"):
            batch_df = df.iloc[i:i + batch_size]

            collection.add(
                embeddings=[emb.tolist() for emb in batch_df["embedding"]],
                documents=batch_df["title"].tolist(),
                metadatas=[
                    {
                        "year": row["year"],
                        "n_citation": row["n_citation"],
                        "gov_score": row["gov_score"],
                    }
                    for _, row in batch_df.iterrows()
                ],
                ids=[str(idx + 1) for idx in batch_df.index]
            )

        logger.info("ChromaDB ingestion completed")

    # -------------------------------------------------------------------
    # Query generation
    # -------------------------------------------------------------------
    def generate_queries(self, raw_data_dir, limit=850_000):
        """
        Generate synthetic search queries from word lists.

        Args:
            raw_data_dir (str): Directory containing word category CSV files.
            limit (int): Number of unique queries to generate.

        Returns:
            pd.DataFrame: Generated queries.
        """
        logger.info("Generating synthetic queries")

        categories = ["nouns", "verbs", "adjectives", "participles"]
        words = {}

        for category in categories:
            path = os.path.join(raw_data_dir, f"{category}.csv")
            words[category] = (
                pd.read_csv(path, header=None).iloc[:, 0].tolist()
            )

        generated = set()
        pbar = tqdm(total=limit, desc="Query Generation")

        while len(generated) < limit:
            query = (
                f"{random.choice(words['nouns'])} "
                f"{random.choice(words['verbs'])} "
                f"{random.choice(words['adjectives'])} "
                f"{random.choice(words['participles'])}"
            )

            if query not in generated:
                generated.add(query)
                pbar.update(1)

        pbar.close()
        return pd.DataFrame({"query": list(generated)})

    # -------------------------------------------------------------------
    # Query embedding pipeline
    # -------------------------------------------------------------------
    def process_queries(self, raw_dir, output_path, batch_size=128):
        """
        Generate synthetic queries and compute their embeddings.

        Args:
            raw_dir (str): Directory with raw word lists.
            output_path (str): Output pickle file.
            batch_size (int): Encoding batch size.
        """
        df_queries = self.generate_queries(raw_dir)

        logger.info("Encoding query embeddings")
        embeddings = self.model.encode(
            df_queries["query"].tolist(),
            batch_size=batch_size,
            show_progress_bar=True
        )

        df_queries["embedding"] = list(embeddings)
        df_queries.to_pickle(output_path)

        logger.info(f"Query embeddings saved to {output_path}")


# -------------------------------------------------------------------
# Script entry point
# -------------------------------------------------------------------
if __name__ == "__main__":
    builder = FeatureBuilder()

    ARTICLES_INTERIM = "data/interim/articles_with_score_df.csv"
    TITLES_PICKLE = "data/interim/titles_with_embeddings.pkl"
    CHROMA_DIR = "data/chroma"
    RAW_WORDS_DIR = "data/raw"
    QUERIES_PICKLE = "data/interim/queries_with_embeddings.pkl"

    builder.create_article_embeddings(ARTICLES_INTERIM, TITLES_PICKLE)
    builder.load_to_chroma(TITLES_PICKLE, CHROMA_DIR)
    builder.process_queries(RAW_WORDS_DIR, QUERIES_PICKLE)
