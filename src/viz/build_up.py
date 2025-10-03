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

# Get logger (initialized in source file)
logger = logging.getLogger(__name__)

def create_build_up_plots(
    team: str,
    first_events_df: pd.DataFrame,
    chain_events_df: pd.DataFrame,
    build_up_stats_df: pd.DataFrame,
) -> Optional[plt.Figure]:
    """
    Create progression and turnovers heatmaps with custom zones for a given team.

    Parameters:
    ----------
    team: str
        The team to plot.
    first_events_df: pd.DataFrame
        The first events data to plot.
    chain_events_df: pd.DataFrame
        The chain events data to plot.
    build_up_stats_df: pd.DataFrame
        The build up statistics data to plot.

    Returns:
    --------
    Optional[plt.Figure]
        The build up plots or None if no events found for the team.
    """

    # Filter events for the team
    first_events_df = first_events_df[first_events_df["team"] == team]
    chain_events_df = chain_events_df[chain_events_df["team"] == team]
    build_up_stats_df = build_up_stats_df[build_up_stats_df["team"] == team]

    if len(first_events_df) == 0:
        logger.error(f"No first events found for {team}")
        return None

    if len(chain_events_df) == 0:
        logger.error(f"No chain events found for {team}")
        return None

    if len(build_up_stats_df) == 0:
        logger.error(f"No build up stats found for {team}")
        return None

    logger.info(f"Creating build up plots for {team}.")

    # Get the number of games played
    games_played = first_events_df["match_id"].nunique()
    
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
    fig = plt.figure(figsize=(11, 11))
    gs = fig.add_gridspec(3, 2, height_ratios=[0.05, 0.92, 0.03])

    # Init axis
    heading_ax = fig.add_subplot(gs[0, :])
    first_events_ax = fig.add_subplot(gs[1, 0])
    chain_events_ax = fig.add_subplot(gs[1, 1])
    legend_ax = fig.add_subplot(gs[2, :])

    # Hide axis
    heading_ax.axis('off')
    first_events_ax.axis('off')
    chain_events_ax.axis('off')
    legend_ax.axis('off')

    # Title
    heading_ax.text(0.02, 0, 
        f"How does {team} build up from goal kicks?",
        fontsize=styling.typo['sizes']['h1'],
        fontproperties=styling.fonts['medium_italic'],
        ha='left', 
        va='bottom'
    )

    # Subtitle
    heading_ax.text(0.02, -0.65, 
        f"Data from {games_played} games at Euro 2024", 
        ha='left',
        va='bottom'
    )

    # Plot titles
    heading_ax.text(0.225, -2.5, 
        "First phase", 
        fontsize=styling.typo['sizes']['h2'], 
        fontproperties=styling.fonts['medium_italic'], 
        ha='center', 
        va='bottom'
    )
    heading_ax.text(0.77, -2.5, 
        "Second phase", 
        fontsize=styling.typo['sizes']['h2'], 
        fontproperties=styling.fonts['medium_italic'], 
        ha='center', 
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
    first_events_pitch = VerticalPitch(
        pitch_type=styling.pitch['pitch_type'],
        line_color=styling.pitch['line_color'], 
        linewidth=styling.pitch['linewidth'], 
        goal_type=styling.pitch['goal_type'], 
        corner_arcs=styling.pitch['corner_arcs'],
    )
    first_events_pitch.draw(ax=first_events_ax)

    chain_events_pitch = VerticalPitch(
        pitch_type=styling.pitch['pitch_type'],
        line_color=styling.pitch['line_color'], 
        linewidth=styling.pitch['linewidth'], 
        goal_type=styling.pitch['goal_type'], 
        corner_arcs=styling.pitch['corner_arcs'],
    )
    chain_events_pitch.draw(ax=chain_events_ax)

    # Plot passes
    plot_passes(first_events_pitch, first_events_df, first_events_ax)
    plot_passes(chain_events_pitch, chain_events_df[chain_events_df["phase"] == 2], chain_events_ax)

    # First events legend    
    legend_ax.text(0.225, 5.5, 
        f"All goal kicks from {team}", 
        fontsize=styling.typo['sizes']['label'], 
        ha='center', 
        va='top'
    )

    legend_ax.text(0.1, 3.7, 
        f"{build_up_stats_df['first_short_pct'].values[0]}%", 
        fontsize=styling.typo['sizes']['h3'], 
        fontproperties=styling.fonts['medium_italic'],
        color=styling.colors['blue'],
        ha='center', 
        va='top'
    )
    
    legend_ax.text(0.1, 2.25, 
        f"{build_up_stats_df['first_short'].values[0]} short passes", 
        fontsize=styling.typo['sizes']['label'], 
        color=styling.colors['blue'],
        ha='center', 
        va='top'
    )
    
    legend_ax.text(0.1, 1.5, 
        f"{build_up_stats_df['first_completed_short_pct'].values[0]}% completed", 
        fontsize=styling.typo['sizes']['label'], 
        color=styling.colors['blue'],
        ha='center', 
        va='top'
    )

    legend_ax.text(0.35, 3.7, 
        f"{build_up_stats_df['first_long_pct'].values[0]}%", 
        fontsize=styling.typo['sizes']['h3'], 
        fontproperties=styling.fonts['medium_italic'],
        color=styling.colors['danger'],
        ha='center', 
        va='top'
    )
    
    legend_ax.text(0.35, 2.25, 
        f"{build_up_stats_df['first_long'].values[0]} long passes", 
        fontsize=styling.typo['sizes']['label'], 
        color=styling.colors['danger'],
        ha='center', 
        va='top'
    )
    
    legend_ax.text(0.35, 1.5, 
        f"{build_up_stats_df['first_completed_long_pct'].values[0]}% completed", 
        fontsize=styling.typo['sizes']['label'], 
        color=styling.colors['danger'],
        ha='center', 
        va='top'
    )
    
    # Second phase legend    
    legend_ax.text(0.77, 5.5, 
        "First pass following a goal kick that doesn't start with the goalkeeper", 
        fontsize=styling.typo['sizes']['label'], 
        ha='center', 
        va='top'
    )
    
    legend_ax.text(0.65, 3.7, 
        f"{build_up_stats_df['second_short_pct'].values[0]}%", 
        fontsize=styling.typo['sizes']['h3'], 
        fontproperties=styling.fonts['medium_italic'],
        color=styling.colors['blue'],
        ha='center', 
        va='top'
    )
    
    legend_ax.text(0.65, 2.25, 
        f"{build_up_stats_df['second_short'].values[0]} short passes", 
        fontsize=styling.typo['sizes']['label'], 
        color=styling.colors['blue'],
        ha='center', 
        va='top'
    )
    
    legend_ax.text(0.65, 1.5, 
        f"{build_up_stats_df['second_completed_short_pct'].values[0]}% completed", 
        fontsize=styling.typo['sizes']['label'], 
        color=styling.colors['blue'],
        ha='center', 
        va='top'
    )

    legend_ax.text(0.9, 3.7, 
        f"{build_up_stats_df['second_long_pct'].values[0]}%", 
        fontsize=styling.typo['sizes']['h3'], 
        fontproperties=styling.fonts['medium_italic'],
        color=styling.colors['danger'],
        ha='center', 
        va='top'
    )
    
    legend_ax.text(0.9, 2.25, 
        f"{build_up_stats_df['second_long'].values[0]} long passes", 
        fontsize=styling.typo['sizes']['label'], 
        color=styling.colors['danger'],
        ha='center', 
        va='top'
    )
    
    legend_ax.text(0.9, 1.5, 
        f"{build_up_stats_df['second_completed_long_pct'].values[0]}% completed", 
        fontsize=styling.typo['sizes']['label'], 
        color=styling.colors['danger'],
        ha='center', 
        va='top'
    )

    # Save plot
    default_kwargs = {
        'bbox_inches': 'tight',
        'pad_inches': 0.25,
        'facecolor': styling.colors['light'],
        'dpi': 300
    }
    output_path = project_root / 'generated_plots' / 'build_up_plots' / f'{team}.png'
    fig.savefig(output_path, **default_kwargs)

    return fig

def plot_passes(
    pitch: VerticalPitch, 
    df: pd.DataFrame, 
    ax: plt.Axes
) -> None:
    """
    Plot passes on a pitch.

    Parameters:
    ----------
    pitch: VerticalPitch
        The pitch to plot on.
    df: pd.DataFrame
        The dataframe to plot.
    ax: plt.Axes
        The axis to plot on.

    Returns:
    --------
    None
    """

    # Masks
    mask_complete = df["pass_outcome"].isna()
    mask_short = df["pass_category"] == "short"
    mask_long = df["pass_category"] == "long"

    # Define combinations and their settings
    pass_combinations = [
        (mask_complete & mask_short, styling.colors['blue'], 1.0),
        (mask_complete & mask_long, styling.colors['danger'], 1.0),
        (~mask_complete & mask_short, styling.colors['blue'], styling.alpha),
        (~mask_complete & mask_long, styling.colors['danger'], styling.alpha),
    ]

    # Plot passes
    for mask, color, alpha in pass_combinations:
        # Check if mask has any True values
        if mask.any():
            pitch.arrows(
                df[mask]["x"],
                df[mask]["y"],
                df[mask]["end_x"],
                df[mask]["end_y"],
                width=styling.arrows['width'],
                headwidth=styling.arrows['headwidth'],
                headlength=styling.arrows['headlength'],
                ax=ax,
                color=color,
                alpha=alpha
            )