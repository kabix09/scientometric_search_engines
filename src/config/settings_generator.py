# -*- coding: utf-8 -*-

"""
Experiment settings generator.

This script generates all valid combinations of experiment parameters
and persists them as an immutable configuration file.

Output:
    - data/external/settings.pkl
"""

import itertools
import pickle
import os
import logging


# -------------------------------------------------------------------
# Logging configuration
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# -------------------------------------------------------------------
# Settings generation
# -------------------------------------------------------------------
def generate_all_settings():
    """
    Generate all valid combinations of experiment parameters.

    Parameters:
        - N: page size
        - k: number of sampled papers
        - pn: weight vector for ranking criteria

    Returns:
        list[dict]: List of experiment configurations.
    """
    page_sizes = [10, 100]
    citation_numbers = [10, 25, 50]

    weights = [0.0, 0.1, 0.25, 0.33, 0.5, 0.75, 0.9, 1.0]

    all_combinations = itertools.product(weights, repeat=4)

    valid_weight_vectors = [
        list(c)
        for c in all_combinations
        if 0.99 <= sum(c) <= 1.0
    ]

    settings = []
    for page_size in page_sizes:
        for citation_number in citation_numbers:
            for weight_vector in valid_weight_vectors:
                settings.append({
                    "N": page_size,
                    "k": citation_number,
                    "pn": weight_vector
                })

    return settings


# -------------------------------------------------------------------
# Script entry point
# -------------------------------------------------------------------
def main():
    """
    Generate and persist experiment settings.

    The script prevents accidental overwriting of existing settings.
    """
    output_path = "data/external/settings.pkl"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if os.path.exists(output_path):
        logger.warning(
            f"Settings file already exists: {output_path}. "
            "Remove it manually to regenerate configurations."
        )
        return

    logger.info("Generating experiment configurations")
    settings = generate_all_settings()

    with open(output_path, "wb") as f:
        pickle.dump(settings, f)

    logger.info(f"Generated {len(settings)} unique configurations")
    logger.info(f"Settings saved to: {output_path}")


if __name__ == "__main__":
    main()
