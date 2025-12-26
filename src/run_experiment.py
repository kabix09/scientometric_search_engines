# -*- coding: utf-8 -*-

"""
Experiment entry point.

This script initializes and runs a batch simulation experiment.
It loads immutable experiment settings, ensures reproducibility,
and executes the experiment in batch mode with checkpoint recovery.

Inputs:
    - data/external/settings.pkl
    - data/interim/queries_with_embeddings.pkl

Outputs:
    - data/results/{config_id}/results.csv
    - data/processed/global_distributions.csv
"""

import os
import pickle
import logging
import numpy as np

from src.models.experiment import Experiment


# -------------------------------------------------------------------
# Logging configuration
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# -------------------------------------------------------------------
# Main execution
# -------------------------------------------------------------------
def main():
    """
    Execute a single batch of the simulation experiment.

    The script:
    1. Loads immutable experiment settings.
    2. Sets a global random seed for reproducibility.
    3. Initializes the experiment orchestrator.
    4. Runs a batch with automatic checkpoint recovery.
    """
    settings_path = "data/external/settings.pkl"

    # -------------------------------------------------------------------
    # Settings validation
    # -------------------------------------------------------------------
    if not os.path.exists(settings_path):
        logger.error(f"Missing settings file: {settings_path}")
        logger.info(
            "Generate settings first using: "
            "src/config/settings_generator.py"
        )
        return

    with open(settings_path, "rb") as f:
        settings = pickle.load(f)

    logger.info(f"Loaded {len(settings)} immutable experiment configurations")

    # -------------------------------------------------------------------
    # Reproducibility
    # -------------------------------------------------------------------
    np.random.seed(42)

    # -------------------------------------------------------------------
    # Experiment initialization
    # -------------------------------------------------------------------
    experiment = Experiment(settings)

    # -------------------------------------------------------------------
    # Batch execution
    # -------------------------------------------------------------------
    try:
        experiment.run_experiment(batch=40_000)
    except Exception as e:
        logger.error(f"Batch execution failed: {e}")
        raise


# -------------------------------------------------------------------
# Script entry point
# -------------------------------------------------------------------
if __name__ == "__main__":
    main()
