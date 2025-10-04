import pandas as pd
import numpy as np
import logging
from sklearn.cluster import KMeans

# Get logger (initialized in source file)
logger = logging.getLogger(__name__)

def transform_to_box_entry_clusters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform box entry events to box entry clusters.

    Parameters:
    ----------
    df: pd.DataFrame
        The box entry events data to transform.

    Returns:
    --------
    clusters_df: pd.DataFrame
        The transformed box entry clusters.
    """

    df = df.copy()

    logger.info(f"Transforming {len(df)} records from box entry events data to box entry clusters.")

    # Calculate clusters (would take )
    kmeans = KMeans(n_clusters=3, random_state=42)
    df["cluster"] = kmeans.fit_predict(df[["x", "y"]])

    # Create clusters dataframe
    clusters_df = df.groupby("cluster").agg({
        "x": "mean",
        "y": "mean",
        "end_x": "mean",
        "end_y": "mean",
        "id": "count",
    }).reset_index()

    logger.info(f"Transformed box entries into {len(clusters_df)} clusters.")
    
    return clusters_df