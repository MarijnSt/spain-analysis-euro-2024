"""Configuration for styling."""

from pathlib import Path
from matplotlib import font_manager
from typing import Dict

class StylingConfig:
    @staticmethod
    def _load_fonts() -> Dict:
        """Load custom fonts from static directory."""
        project_root = Path.cwd()
        font_base_path = project_root / 'static' / 'fonts'
        
        font_paths = {
            'light': font_base_path / 'Futura-Light.ttf',
            'medium': font_base_path / 'Futura-Medium.ttf',
            'medium_italic': font_base_path / 'Futura-MediumItalic.ttf',
            'bold': font_base_path / 'Futura-Bold.ttf',
            'condensed_medium': font_base_path / 'Futura-CondensedMedium.ttf',
            'condensed_bold': font_base_path / 'Futura-CondensedExtraBold.ttf',
        }

        fonts = {}

        for name, path in font_paths.items():
            if path.exists():
                font_manager.fontManager.addfont(str(path))
                fonts[name] = font_manager.FontProperties(fname=str(path))

        return fonts

    # Custom fonts
    fonts = _load_fonts()

    # Theme colors
    colors = {
        'primary': '#053225',
        'light': '#f2f4ee',
        'secondary': '#DC851F',
        'info': '#6D98BA',
        'danger': '#CA2E55',
        'white': '#FFFFFF',
    }

    # Typography
    typo = {
        'sizes': {
            'h1': 20,
            'h2': 18,
            'h3': 16,
            'p': 12,
            'label': 8,
        },
        'alpha': 0.2,
    }

styling = StylingConfig()