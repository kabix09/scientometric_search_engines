# -*- coding: utf-8 -*-

"""
Dataset construction script.

This script:
1. Loads the official Polish Ministry journal and conference scoring lists (Excel).
2. Loads raw DBLP publication data (JSON lines).
3. Matches publications with ministerial venues.
4. Produces a cleaned dataset enriched with government scores.

Output:
    data/interim/articles_with_score_df.csv
"""

import os
import json
import logging
import pandas as pd
import numpy as np
from tqdm import tqdm


# -------------------------------------------------------------------
# Logging configuration (recommended for src-level scripts)
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# -------------------------------------------------------------------
# Government (ministerial) data loading
# -------------------------------------------------------------------
def load_gov_data(excel_path):
    """
    Load and clean official ministerial lists of journals and conferences.

    Args:
        excel_path (str): Path to the Excel file containing ministerial data.

    Returns:
        tuple:
            - journal_lookup (dict): Journal title → score
            - conference_lookup (dict): Conference name → score
    """
    logger.info("Loading ministerial journal and conference lists...")

    # ---- Journals (sheet 0) ----
    gov_articles_data = pd.read_excel(excel_path, sheet_name=0, header=None)

    # Merge header rows into a single header
    gov_articles_data.columns = np.where(
        gov_articles_data.iloc[0].notna(),
        gov_articles_data.iloc[0].astype(str) + ' - ' + gov_articles_data.iloc[1].astype(str),
        gov_articles_data.iloc[1]
    )

    gov_articles_data = gov_articles_data[2:].reset_index(drop=True)

    journals_list = gov_articles_data[['Tytuł 2', 'Punkty']]
    journals_list = journals_list.drop_duplicates(subset=['Tytuł 2']).dropna()

    journal_lookup = journals_list.set_index('Tytuł 2').to_dict(orient='index')

    # ---- Conferences (sheet 1) ----
    gov_conferences_data = pd.read_excel(excel_path, sheet_name=1)
    gov_conferences_data['Przypisane dyscypliny naukowe'] = (
        gov_conferences_data['Przypisane dyscypliny naukowe']
        .replace('\n', ' ', regex=True)
    )

    conferences_list = gov_conferences_data[['Nazwa konferencji', 'Liczba punktów']]
    conferences_list = conferences_list.drop_duplicates(subset=['Nazwa konferencji']).dropna()

    conference_lookup = conferences_list.set_index('Nazwa konferencji').to_dict(orient='index')

    return journal_lookup, conference_lookup


# -------------------------------------------------------------------
# DBLP raw data loading
# -------------------------------------------------------------------
def load_dblp_raw_data(directory_path):
    """
    Load raw DBLP publications from JSON files.

    Each file is expected to be in JSON Lines format.

    Args:
        directory_path (str): Directory containing DBLP JSON files.

    Returns:
        list: List of publication dictionaries.
    """
    logger.info(f"Loading DBLP publications from: {directory_path}")
    publications = []

    try:
        file_names = [f for f in os.listdir(directory_path) if f.endswith('.json')]

        for file_name in file_names:
            logger.info(f"Processing file: {file_name}")

            with open(os.path.join(directory_path, file_name), 'r', encoding='utf-8') as f:
                for line in tqdm(f, desc=f"Loading {file_name}"):
                    pub = json.loads(line)

                    # Ensure required keys exist
                    pub.setdefault('references', [])
                    pub.setdefault('authors', [])
                    pub.setdefault('venue', '')

                    publications.append(pub)

        return publications

    except Exception as e:
        logger.error(f"Error while loading DBLP data: {e}")
        return []


# -------------------------------------------------------------------
# Main data transformation pipeline
# -------------------------------------------------------------------
def main(input_excel, dblp_dir, output_file):
    """
    Execute the full data processing pipeline.

    Steps:
        1. Load ministerial scoring data.
        2. Load raw DBLP publications.
        3. Match venues and assign scores.
        4. Save enriched dataset to CSV.
    """
    journal_lookup, conference_lookup = load_gov_data(input_excel)
    publications = load_dblp_raw_data(dblp_dir)

    logger.info("Merging DBLP data with ministerial scores...")
    processed_publications = []

    for pub in tqdm(publications, desc="Merging"):
        venue = pub.get('venue', '')
        score = None

        if venue in conference_lookup:
            score = conference_lookup[venue]['Liczba punktów']
        elif venue in journal_lookup:
            score = journal_lookup[venue]['Punkty']

        if score is not None:
            processed_publications.append({
                "id": pub.get("id"),
                "title": pub.get("title"),
                "year": pub.get("year"),
                "references": pub.get("references"),
                "authors": pub.get("authors"),
                "n_citation": pub.get("n_citation"),
                "venue": venue,
                "gov_score": score
            })

    # Free memory
    del publications

    logger.info(f"Saving {len(processed_publications)} records to {output_file}")
    df_final = pd.DataFrame(processed_publications)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df_final.to_csv(output_file, index=False)

    logger.info("Dataset construction completed successfully.")


# -------------------------------------------------------------------
# Script entry point
# -------------------------------------------------------------------
if __name__ == "__main__":
    INPUT_EXCEL = "data/external/Wykaz_dyscyplin_do_czasopism_i_materiałów_konferencyjnych.xlsx"
    DBLP_DIRECTORY = "data/external/dblp-ref-10"
    OUTPUT_CSV = "data/interim/articles_with_score_df.csv"

    main(INPUT_EXCEL, DBLP_DIRECTORY, OUTPUT_CSV)
