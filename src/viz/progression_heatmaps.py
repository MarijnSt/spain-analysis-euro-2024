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

def create_progression_heatmaps(
    team: str,
    prog_actions_df: pd.DataFrame,
    turnovers_df: pd.DataFrame,
) -> Optional[plt.Figure]:
    """
    Create progression and turnovers heatmaps with custom zones for a given team.

    Parameters:
    ----------
    team: str
        The team to plot.
    prog_actions_df: pd.DataFrame
        The progressive actions data to plot.
    turnovers_df: pd.DataFrame
        The turnovers data to plot.

    Returns:
    --------
    Optional[plt.Figure]
        The progression and turnovers heatmaps or None if no events found for the team.
    """

    # Filter events for the team
    prog_actions_df = prog_actions_df[prog_actions_df["team"] == team]
    turnovers_df = turnovers_df[turnovers_df["team"] == team]

    if len(prog_actions_df) == 0:
        logger.error(f"No progressive actions found for {team}")
        return None

    if len(turnovers_df) == 0:
        logger.error(f"No turnovers found for {team}")
        return None

    logger.info(f"Creating progression heatmaps for {team}.")

    # Get the number of games played
    games_played = prog_actions_df["match_id"].nunique()
    
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
    prog_ax = fig.add_subplot(gs[1, 0])
    turnover_ax = fig.add_subplot(gs[1, 1])
    legend_ax = fig.add_subplot(gs[2, :])

    # Hide axis
    heading_ax.axis('off')
    prog_ax.axis('off')
    turnover_ax.axis('off')
    legend_ax.axis('off')

    # Title
    heading_ax.text(0.02, 0, 
        f"Where does {team} move and lose the ball?",
        fontsize=styling.typo['sizes']['h1'],
        fontproperties=styling.fonts['medium_italic'],
        ha='left', 
        va='bottom'
    )

    # Subtitle
    heading_ax.text(0.02, -0.65, 
        f"In build up and progression zones from {games_played} games at Euro 2024", 
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
    prog_pitch = VerticalPitch(
        pitch_type=styling.pitch['pitch_type'],
        line_color=styling.pitch['line_color'], 
        linewidth=styling.pitch['linewidth'], 
        goal_type=styling.pitch['goal_type'], 
        corner_arcs=styling.pitch['corner_arcs'],
    )
    prog_pitch.draw(ax=prog_ax)

    turnover_pitch = VerticalPitch(
        pitch_type=styling.pitch['pitch_type'],
        line_color=styling.pitch['line_color'], 
        linewidth=styling.pitch['linewidth'], 
        goal_type=styling.pitch['goal_type'], 
        corner_arcs=styling.pitch['corner_arcs'],
    )
    turnover_pitch.draw(ax=turnover_ax)

    # Create heatmaps
    create_heatmap(prog_pitch, prog_actions_df, prog_ax, "Reds")
    create_heatmap(turnover_pitch, turnovers_df, turnover_ax, "Greens")

    # Progressive actions legend
    legend_ax.text(0.225, 3, 
        "Progressive actions", 
        fontsize=styling.typo['sizes']['h2'], 
        fontproperties=styling.fonts['medium_italic'], 
        ha='center', 
        va='bottom'
    )
    
    legend_ax.text(0.225, 2.5, 
        "Passes and carries that progress the ball\nby at least 10 metres", 
        fontsize=styling.typo['sizes']['p'], 
        ha='center', 
        va='top'
    )
    
    # Turnovers legend
    legend_ax.text(0.77, 3, 
        "Turnovers", 
        fontsize=styling.typo['sizes']['h2'], 
        fontproperties=styling.fonts['medium_italic'], 
        ha='center', 
        va='bottom'
    )
    
    legend_ax.text(0.77, 2.5, 
        "Passes, dribbles, receptions and duels\nthat lead to a loss of possession", 
        fontsize=styling.typo['sizes']['p'], 
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
    output_path = project_root / 'generated_plots' / 'progression_heatmaps' / f'{team}.png'
    fig.savefig(output_path, **default_kwargs)

    return fig


    

def create_heatmap(
    pitch: VerticalPitch,
    df: pd.DataFrame,
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
        alpha=0.7,
        zorder=0,
    )

    # Zone lines (horizontal lines for x coordinates, vertical lines for y coordinates because of pitch orientation)
    for x in x_coords:
        ax.plot([0, 80], [x, x], color=styling.colors['primary'], linewidth=0.5, 
                     linestyle='--', dashes=(5, 15), alpha=0.5)
    for y in y_coords:
        ax.plot([y, y], [0, 120], color=styling.colors['primary'], linewidth=0.5, 
                     linestyle='--', dashes=(5, 15), alpha=0.5)
    