import logging
from token import OP
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional

from src.config import styling
from src.transform import transform_to_box_entry_clusters

# Get logger (initialized in source file)
logger = logging.getLogger(__name__)

def create_box_entry_plots(
    team: str,
    box_entries_df: pd.DataFrame,
) -> Optional[plt.Figure]:
    """
    Create box entry heatmaps with custom zones for a given team.

    Parameters:
    ----------
    team: str
        The team to plot.
    box_entries_df: pd.DataFrame
        The box entry data to plot.

    Returns:
    --------
    Optional[plt.Figure]
        The box entry heatmaps or None if no events found for the team.
    """

    # Filter events for the team
    box_entries_df = box_entries_df[box_entries_df["team"] == team]
    team_passes_df = box_entries_df[box_entries_df["type"] == "Pass"]
    team_carries_df = box_entries_df[box_entries_df["type"] == "Carry"]

    if len(box_entries_df) == 0:
        logger.error(f"No box entries found for {team}")
        return None

    if len(team_passes_df) == 0:
        logger.error(f"No box entrypasses found for {team}")
        return None

    if len(team_carries_df) == 0:
        logger.error(f"No box entry carries found for {team}")
        return None

    # Create clusters
    team_carries_clusters = transform_to_box_entry_clusters(team_carries_df)
    team_passes_clusters = transform_to_box_entry_clusters(team_passes_df)

    logger.info(f"Creating box entry plots for {team}.")
    logger.info(f"Box entry carries: {len(team_carries_df)}")
    logger.info(f"Box entry passes: {len(team_passes_df)}")
    logger.info(f"Box entry carries clusters: {len(team_carries_clusters)}")
    logger.info(f"Box entry passes clusters: {len(team_passes_clusters)}")

    # Get the number of games played
    games_played = box_entries_df["match_id"].nunique()
    
    # Init plt styling
    plt.rcParams.update({
        'font.family': styling.fonts['light'].get_name(),
        'font.size': styling.typo['sizes']['p'],
        'text.color': styling.colors['primary'],
        'axes.labelcolor': styling.colors['primary'],
        'axes.edgecolor': styling.colors['primary'],
        'xtick.color': styling.colors['primary'],
        'ytick.color': styling.colors['primary'],
        'grid.color': styling.colors['primary'],
        'figure.facecolor': styling.colors['light'],
        'axes.facecolor': styling.colors['light'],
    })

    # Create figure
    fig = plt.figure(figsize=(11, 7))
    gs = fig.add_gridspec(3, 2, height_ratios=[0.1, 0.98, 0.1])

    # Init axis
    heading_ax = fig.add_subplot(gs[0, :])
    carries_ax = fig.add_subplot(gs[1, 0])
    passes_ax = fig.add_subplot(gs[1, 1])
    legend_ax = fig.add_subplot(gs[2, :])

    # Hide axis
    heading_ax.axis('off')
    carries_ax.axis('off')
    passes_ax.axis('off')
    legend_ax.axis('off')

    # Title
    heading_ax.text(0.02, 0, 
        f"How does {team} enter the box?",
        fontsize=styling.typo['sizes']['h1'],
        fontproperties=styling.fonts['medium_italic'],
        ha='left', 
        va='bottom'
    )

    # Subtitle
    heading_ax.text(0.02, -0.65, 
        f"Open play box entries* from {games_played} games at Euro 2024",
        ha='left',
        va='bottom'
    )

    # Euro 2024 logo
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    logo_path = project_root / 'static' / 'euro_2024_logo.png'
    logo = mpimg.imread(logo_path)
    imagebox = OffsetImage(logo, zoom=0.15)
    ab = AnnotationBbox(
        imagebox, 
        (0.98, -0.65),                     # location of annotation box
        xycoords='axes fraction',   # use axes fraction coordinates: relative to axes and percentage of axes for position
        box_alignment=(1, 0),       # alignment of the annotation box: (1, 0) means right-aligned and bottom-aligned
        frameon=False               # don't show the frame of the annotation box
    )
    heading_ax.add_artist(ab)

    # Pitches
    carries_pitch = VerticalPitch(
        pitch_type=styling.pitch['pitch_type'],
        line_color=styling.pitch['line_color'], 
        linewidth=styling.pitch['linewidth'], 
        goal_type=styling.pitch['goal_type'], 
        corner_arcs=styling.pitch['corner_arcs'],
        half=True,
        pad_bottom=0.1
    )
    carries_pitch.draw(ax=carries_ax)

    passes_pitch = VerticalPitch(
        pitch_type=styling.pitch['pitch_type'],
        line_color=styling.pitch['line_color'], 
        linewidth=styling.pitch['linewidth'], 
        goal_type=styling.pitch['goal_type'], 
        corner_arcs=styling.pitch['corner_arcs'],
        half=True,
        pad_bottom=0.1
    )
    passes_pitch.draw(ax=passes_ax)

    # Plot heatmaps
    create_heatmap(team_carries_df, carries_pitch, carries_ax, "Blues")
    create_heatmap(team_passes_df, passes_pitch, passes_ax, "Blues")

    # Plot actions
    plot_actions(team_carries_df, carries_pitch, carries_ax)
    plot_actions(team_passes_df, passes_pitch, passes_ax)

    # Plot cluster arrows
    plot_cluster_arrows(team_carries_clusters, carries_pitch, carries_ax)
    plot_cluster_arrows(team_passes_clusters, passes_pitch, passes_ax)

    legend_ax.text(0.02, 0.5, 
        f"*Solid arrows indicate the top 5 most common clusters per action.", 
        fontsize=styling.typo['sizes']['p'], 
        ha='left', 
        va='center'
    )

    # Plot titles for actions
    legend_ax.text(0.225, 1.75, 
        "Carries", 
        fontsize=styling.typo['sizes']['h2'], 
        fontproperties=styling.fonts['medium_italic'], 
        ha='center', 
        va='bottom'
    )
    legend_ax.text(0.77, 1.75, 
        "Passes", 
        fontsize=styling.typo['sizes']['h2'], 
        fontproperties=styling.fonts['medium_italic'], 
        ha='center', 
        va='bottom'
    )

    # Save plot
    default_kwargs = {
        'bbox_inches': 'tight',
        'pad_inches': 0.25,
        'facecolor': styling.colors['light'],
        'dpi': 300
    }
    output_path = project_root / 'generated_plots' / 'box_entry_plots' / f'{team}.png'
    fig.savefig(output_path, **default_kwargs)

    return fig


    

def create_heatmap(
    df: pd.DataFrame,
    pitch: VerticalPitch,
    ax: plt.Axes,
    cmap: str = 'Reds',
) -> None:
    """
    Create a heatmap for a given dataframe.

    Parameters:
    ----------
    pitch: VerticalPitch
        The pitch to plot on.
    df: pd.DataFrame
        The dataframe to plot.
    ax: plt.Axes
        The axis to plot on.
    cmap: str
        The colormap to use.

    Returns:
    --------
    None
    """

    # Custom zones
    x_coords = [0, 18, 40, 60, 80, 102, 120]
    y_coords = [0, 18, 30, 50, 62, 80]

    # Get coordinates
    x_data = df["x"].values
    y_data = df["y"].values

    # Create custom bin edges
    x_bins = np.array([0, 18, 40, 60, 80, 102, 120])
    y_bins = np.array([0, 18, 30, 50, 62, 80])

    # Use mplsoccer's bin_statistic with custom bins
    stats = pitch.bin_statistic(
        x_data, y_data, 
        bins=[x_bins, y_bins],
        statistic='count'
    )

    # Create heatmap using mplsoccer's heatmap function
    pitch.heatmap(
        stats=stats,
        ax=ax,
        cmap=cmap,
        alpha=0.5,
        zorder=0,
    )

    # Zone lines (horizontal lines for x coordinates, vertical lines for y coordinates because of pitch orientation)
    for x in x_coords:
        ax.plot([0, 80], [x, x], color=styling.colors['primary'], linewidth=0.5, 
                     linestyle='--', dashes=(5, 15), alpha=0.5)
    for y in y_coords:
        ax.plot([y, y], [0, 120], color=styling.colors['primary'], linewidth=0.5, 
                     linestyle='--', dashes=(5, 15), alpha=0.5)
    

def plot_actions(
    df: pd.DataFrame,
    pitch: VerticalPitch,
    ax: plt.Axes,
) -> None:
    """
    Plot actions on a pitch.

    Parameters:
    ----------
    df: pd.DataFrame
        The dataframe of actions to plot.
    pitch: VerticalPitch
        The pitch to plot on.
    ax: plt.Axes
        The axis to plot on.
    """

    # Plot actions
    pitch.arrows(
        df["x"],
        df["y"],
        df["end_x"],
        df["end_y"],
        width=styling.arrows['width'],
        headwidth=styling.arrows['headwidth'],
        headlength=styling.arrows['headlength'],
        ax=ax,
        alpha=0.1,
    )


def plot_cluster_arrows(
    df: pd.DataFrame,
    pitch: VerticalPitch,
    ax: plt.Axes,
) -> None:
    """
    Plot actions on a pitch.

    Parameters:
    ----------
    df: pd.DataFrame
        The dataframe of clusters to plot.
    pitch: VerticalPitch
        The pitch to plot on.
    ax: plt.Axes
        The axis to plot on.
    """

    # Plot actions
    pitch.arrows(
        df["x"],
        df["y"],
        df["end_x"],
        df["end_y"],
        width=styling.arrows['width'],
        headwidth=styling.arrows['headwidth'],
        headlength=styling.arrows['headlength'],
        ax=ax,
    )
    