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
    data: pd.DataFrame,
) -> plt.Figure:
    """
    Create a plot of the distribution of the goalkeeper's actions.

    Parameters:
    ----------
    data: pd.DataFrame
        The data to plot.

    Returns:
    --------
    plt.Figure
        The plot of the distribution of the goalkeeper's actions.
    """

    logger.info(f"Creating goal kick distribution plot!")
    
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
    gs = fig.add_gridspec(3, 1, height_ratios=[0.1, 0.85, 0.05])       # 2 rows, 1 column, with height ratios for title, plot and legend

    # Init axis
    heading_ax = fig.add_subplot(gs[0])
    main_ax = fig.add_subplot(gs[1])
    legend_ax = fig.add_subplot(gs[2])

    # Hide axis
    heading_ax.axis('off')

    # Hide spines
    # main_ax.spines['top'].set_visible(False)
    # main_ax.spines['bottom'].set_visible(False)
    # main_ax.spines['left'].set_visible(False)
    # main_ax.spines['right'].set_visible(False)

    # Remove axis ticks
    # main_ax.set_yticklabels([])
    # main_ax.set_yticks([])
    # main_ax.set_xticks([])

    # Title
    heading_ax.text(
        0, 
        0.45, 
        f"Spain's distribution from goal kicks",
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

    return fig