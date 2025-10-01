import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
from pathlib import Path
import pandas as pd
import logging

from src.config import styling

# Get logger (initialized in source file)
logger = logging.getLogger(__name__)

def create_gk_distribution_plot(
    team: str,
    events_df: pd.DataFrame,
    stats_df: pd.DataFrame
) -> plt.Figure:
    """
    Create a plot of the distribution of the goalkeeper's actions.

    Parameters:
    ----------
    team: str
        The team to plot.
    events_df: pd.DataFrame
        The goal kicks to plot.
    stats_df: pd.DataFrame
        The team stats for the goal kicks.

    Returns:
    --------
    plt.Figure
        The plot of the distribution of the goalkeeper's actions.
    """

    # Filter events and stats for the team
    events_df = events_df[events_df["team"] == team]
    stats_df = stats_df[stats_df["team"] == team]

    if len(events_df) == 0:
        logger.error(f"No events found for {team}")
        return None
    
    if len(stats_df) == 0:
        logger.error(f"No stats found for {team}")
        return None

    logger.info(f"Creating goal kick distribution plot for {team}")
    
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
    fig = plt.figure(figsize=(11, 12))
    gs = fig.add_gridspec(2, 2, height_ratios=[0.1, 0.9], width_ratios=[0.7, 0.3])       # 2 rows, 2 columns, with height ratios for rows and width ratios for columns

    # Init axis
    heading_ax = fig.add_subplot(gs[0, :])
    main_ax = fig.add_subplot(gs[1, 0])
    legend_ax = fig.add_subplot(gs[1, 1])

    # Hide axis
    heading_ax.axis('off')
    # main_ax.axis('off')
    legend_ax.axis('off')

    # Title
    heading_ax.text(0, 0.45, f"{team}'s distribution from goal kicks",
        fontsize=styling.typo['sizes']['h1'],
        fontproperties=styling.fonts['medium_italic'],
        ha='left', 
        va='bottom'
    )

    # Subtitle
    heading_ax.text(
        0, 
        0, 
        f'Goalkick end locations from all Euro 2024 games', 
        ha='left',
        va='bottom'
    )

    # Euro 2024 logo
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    logo_path = project_root / 'static' / 'euro_2024_logo.png'
    logo = mpimg.imread(logo_path)
    imagebox = OffsetImage(logo, zoom=0.2)
    ab = AnnotationBbox(
        imagebox, 
        (1, 0),                     # location of annotation box
        xycoords='axes fraction',   # use axes fraction coordinates: relative to axes and percentage of axes for position
        box_alignment=(1, 0),       # alignment of the annotation box: (1, 0) means right-aligned and bottom-aligned
        frameon=False               # don't show the frame of the annotation box
    )
    heading_ax.add_artist(ab)

    # Pitch
    pitch = VerticalPitch(
        pitch_type=styling.pitch['pitch_type'],
        line_color=styling.pitch['line_color'], 
        linewidth=styling.pitch['linewidth'], 
        half=styling.pitch['half'], 
        goal_type=styling.pitch['goal_type'], 
        corner_arcs=styling.pitch['corner_arcs']
    )
    pitch.draw(ax=main_ax)

    # Create masks
    mask_complete = events_df["pass_outcome"] == "Complete"
    mask_short = events_df["pass_length"] == "short"
    mask_long = events_df["pass_length"] == "long"

    # Define combinations and their settings
    pass_combinations = [
        (mask_complete & mask_short, styling.colors['info'], 1.0),
        (mask_complete & mask_long, styling.colors['danger'], 1.0),
        (~mask_complete & mask_short, styling.colors['info'], styling.alpha),
        (~mask_complete & mask_long, styling.colors['danger'], styling.alpha),
    ]

    # Plot passes
    for mask, color, alpha in pass_combinations:
        # Check if mask has any True values
        if mask.any():
            pitch.arrows(
                events_df[mask]["x"],
                events_df[mask]["y"],
                events_df[mask]["end_x"],
                events_df[mask]["end_y"],
                width=styling.arrows['width'],
                headwidth=styling.arrows['headwidth'],
                headlength=styling.arrows['headlength'],
                ax=main_ax,
                color=color,
                alpha=alpha
            )

    # Long passes legend
    legend_ax.text(0, 0.675, f"{stats_df['long_percentage'].values[0]}%", 
        fontsize=styling.typo['sizes']['h0'],
        fontproperties=styling.fonts['medium_italic'],
        color=styling.colors['danger'],
        ha='left', 
        va='bottom'
    )

    legend_ax.text(0, 0.625, f"{stats_df['long_passes'].values[0]} long passes",
        fontsize=styling.typo['sizes']['h3'],
        color=styling.colors['danger'],
        ha='left', 
        va='bottom'
    )

    legend_ax.text(0, 0.575, f"{stats_df['completed_long_percentage'].values[0]}% completed", 
        fontsize=styling.typo['sizes']['h3'],
        color=styling.colors['danger'],
        ha='left', 
        va='bottom'
    )

    # Short passes legend
    legend_ax.text(0, 0.325, f"{stats_df['short_percentage'].values[0]}%", 
        fontsize=styling.typo['sizes']['h0'],
        fontproperties=styling.fonts['medium_italic'],
        color=styling.colors['info'],
        ha='left', 
        va='bottom'
    )

    legend_ax.text(0, 0.275, f"{stats_df['short_passes'].values[0]} short passes",
        fontsize=styling.typo['sizes']['h3'],
        color=styling.colors['info'],
        ha='left', 
        va='bottom'
    )

    legend_ax.text(0, 0.225, f"{stats_df['completed_short_percentage'].values[0]}% completed", 
        fontsize=styling.typo['sizes']['h3'],
        color=styling.colors['info'],
        ha='left', 
        va='bottom'
    )

    return fig