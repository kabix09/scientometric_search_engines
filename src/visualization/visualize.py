# -*- coding: utf-8 -*-

"""
Scientometrics distribution analysis.

This module provides:
- Transformation of article-level counters into citation distributions
- Statistical comparison using Kolmogorov–Smirnov tests
- Power-law compatible Zipf (log-log) visualizations
- Batch PDF report generation for all experiment configurations
"""

import ast
import collections
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import powerlaw

from scipy.stats import ks_2samp
from matplotlib.backends.backend_pdf import PdfPages


# -------------------------------------------------------------------
# Data loading
# -------------------------------------------------------------------
def load_results(processed_path="data/processed/global_distributions.csv"):
    """
    Load aggregated experiment results.

    Parameters:
        processed_path (str): Path to CSV with global distributions.

    Returns:
        pd.DataFrame: Parsed results with Python objects restored.
    """
    df = pd.read_csv(processed_path)
    df["settings"] = df["settings"].apply(ast.literal_eval)
    df["distribution"] = df["distribution"].apply(ast.literal_eval)
    return df


# -------------------------------------------------------------------
# Distribution transformations
# -------------------------------------------------------------------
def get_citation_distribution(counter_dict):
    """
    Convert article-level counts to citation-frequency distribution.

    Input:
        {article_id: citation_count}

    Output:
        {citation_count: frequency}
    """
    return collections.Counter(counter_dict.values())


# -------------------------------------------------------------------
# Statistical analysis
# -------------------------------------------------------------------
def calculate_ks_metrics(dist_citations, reference_dist):
    """
    Compute Kolmogorov–Smirnov statistics between two distributions.

    Parameters:
        dist_citations (dict): Experimental citation distribution
        reference_dist (dict): Empirical/reference distribution

    Returns:
        tuple: (KS statistic, p-value)
    """
    exp_values = list(dist_citations.values())
    ref_values = list(reference_dist.values())

    ks_stat, p_val = ks_2samp(exp_values, ref_values)
    return ks_stat, p_val


# -------------------------------------------------------------------
# Visualization
# -------------------------------------------------------------------
def plot_zipf_comparison(
    exp_dist,
    ref_dist,
    settings_str,
    ks_stat,
    p_val,
    pdf_handle=None
):
    """
    Generate Zipf (log-log) comparison plot for citation distributions.

    Parameters:
        exp_dist (dict): Experimental distribution
        ref_dist (dict): Reference distribution
        settings_str (str): Configuration descriptor
        ks_stat (float): KS statistic
        p_val (float): KS p-value
        pdf_handle (PdfPages, optional): PDF output handler
    """
    exp_data = (
        pd.DataFrame(exp_dist.items(), columns=["Citations", "Count"])
        .sort_values("Citations")
    )
    ref_data = (
        pd.DataFrame(ref_dist.items(), columns=["Citations", "Count"])
        .sort_values("Citations")
    )

    plt.figure(figsize=(12, 8))
    plt.loglog(
        exp_data["Citations"],
        exp_data["Count"],
        "o-",
        label="Simulation",
        markersize=3
    )
    plt.loglog(
        ref_data["Citations"],
        ref_data["Count"],
        "s-",
        label="Empirical",
        markersize=3
    )

    plt.title(f"Zipf Plot — {settings_str}")
    plt.xlabel("Number of citations")
    plt.ylabel("Frequency")
    plt.grid(True, which="both", linestyle="--", alpha=0.5)

    stats_text = f"KS statistic: {ks_stat:.4f}\nP-value: {p_val:.4f}"
    plt.text(
        0.05,
        0.05,
        stats_text,
        transform=plt.gca().transAxes,
        bbox=dict(facecolor="white", alpha=0.85)
    )

    plt.legend()

    if pdf_handle is not None:
        pdf_handle.savefig()
        plt.close()
    else:
        plt.show()


# -------------------------------------------------------------------
# Report generation
# -------------------------------------------------------------------
def generate_report_pdf(
    df,
    reference_dist,
    output_path="reports/figures/full_experiment_report.pdf"
):
    """
    Generate a PDF report containing Zipf plots for all configurations.

    Parameters:
        df (pd.DataFrame): Experiment results
        reference_dist (dict): Empirical citation distribution
        output_path (str): Output PDF path
    """
    with PdfPages(output_path) as pdf:
        for _, row in df.iterrows():
            citation_dist = get_citation_distribution(row["distribution"])
            ks_stat, p_val = calculate_ks_metrics(
                citation_dist,
                reference_dist
            )

            plot_zipf_comparison(
                citation_dist,
                reference_dist,
                settings_str=str(row["settings"]),
                ks_stat=ks_stat,
                p_val=p_val,
                pdf_handle=pdf
            )