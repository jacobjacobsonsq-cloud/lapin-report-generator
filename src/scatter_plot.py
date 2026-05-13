# ===================================================================================
# FILE: src/scatter_plot.py
# High Performing Teams scatter plot - standalone module
# ===================================================================================

import matplotlib
matplotlib.use('Agg', force=True)
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
from io import BytesIO
import os

COLORS = {
    'navy': '#1A1A42',
    'dark_gray': '#8B9197',
}

SCATTER_BG = '#A3BDEE'

STANDARDS_QUESTIONS = [
    "We have a can-do attitude.",
    "We are results driven.",
    "We have high performance expectations in this company.",
    "We effectively address poor performance.",
    "We recognize strong performance.",
]

PSYCH_SAFETY_QUESTIONS = [
    "We speak honestly to each other.",
    "Office politics do not influence behavior.",
    "We willingly accept tough feedback.",
    "We encourage differing viewpoints.",
    "It is safe to speak our minds even when our views could be controversial.",
    "We give each other the benefit of the doubt.",
]

ZONE_LABELS = [
    # (x, y, label)
    (1.67, 4.33, 'Complacent\nZone'),
    (3.00, 4.33, 'Learning\nZone'),
    (4.33, 4.33, 'Excellence\nZone'),
    (1.67, 3.00, 'Apathy Zone'),
    (3.00, 3.00, 'Comfort Zone'),
    (4.33, 3.00, 'Performance\nZone'),
    (1.67, 1.67, 'Frozen Zone'),
    (3.00, 1.67, 'Insecurity\nZone'),
    (4.33, 1.67, 'Anxiety Zone'),
]


class ScatterPlotGenerator:
    def __init__(self, processor):
        self.processor = processor
        self._load_fonts()

    def _load_fonts(self):
        font_medium = os.path.join('assets', 'fonts', 'ginto-normal-medium.otf')
        font_light = os.path.join('assets', 'fonts', 'ginto-normal-light.otf')
        for f in [font_medium, font_light]:
            if os.path.exists(f):
                fm.fontManager.addfont(f)

    def _get_person_scores(self, role=None):
        """Calculate per-person (x=standards avg, y=psych safety avg)."""
        if role:
            data = self.processor.responses[self.processor.responses['Role'] == role].copy()
        else:
            data = self.processor.responses.copy()

        x_vals, y_vals = [], []
        for _, row in data.iterrows():
            std_scores = []
            for q in STANDARDS_QUESTIONS:
                if q in data.columns:
                    s = pd.to_numeric(row[q], errors='coerce')
                    if pd.notna(s):
                        std_scores.append(s)

            psy_scores = []
            for q in PSYCH_SAFETY_QUESTIONS:
                if q in data.columns:
                    s = pd.to_numeric(row[q], errors='coerce')
                    if pd.notna(s):
                        psy_scores.append(s)

            if std_scores and psy_scores:
                x_vals.append(np.mean(std_scores))
                y_vals.append(np.mean(psy_scores))

        return x_vals, y_vals

    def create(self, role=None):
        """Generate the 9-quadrant High Performing Teams scatter plot."""
        fig, ax = plt.subplots(figsize=(8, 3.2))

        x_vals, y_vals = self._get_person_scores(role)

        # --- Background fill for entire bordered area (including tick numbers) ---
        ax.fill_between([0.82, 5.20], 0.62, 5.20, facecolor=SCATTER_BG, alpha=1.0, zorder=0)

        # --- Grid division lines (contained within 1-5) ---
        for y in [2.33, 3.67]:
            ax.plot([1, 5], [y, y], color=COLORS['navy'], linewidth=1.2, alpha=0.7, zorder=1)
        for x in [2.33, 3.67]:
            ax.plot([x, x], [1, 5], color=COLORS['navy'], linewidth=1.2, alpha=0.7, zorder=1)

        # --- Border around the grid + axis numbers ---
        ax.plot([0.82, 5.20, 5.20, 0.82, 0.82], [0.62, 0.62, 5.20, 5.20, 0.62],
                color=COLORS['navy'], linewidth=0.7, alpha=0.4, zorder=1)

        # --- Scatter dots ---
        if x_vals and y_vals:
            ax.scatter(x_vals, y_vals, s=18, alpha=0.95, color=COLORS['navy'],
                       edgecolors=COLORS['navy'], linewidth=0.5, zorder=2)

        # --- Zone labels ---
        for zx, zy, label in ZONE_LABELS:
            ax.text(zx, zy, label, ha='center', va='center',
                    fontsize=11, alpha=1.0, color=COLORS['navy'])

        # --- Axis tick numbers (1-5) along left and bottom edges ---
        for v in [1, 2, 3, 4, 5]:
            # Y-axis numbers (left side, just inside border)
            ax.text(0.93, v, str(v), ha='right', va='center',
                    fontsize=9, color=COLORS['navy'], fontname='Ginto Normal Light')
            # X-axis numbers (bottom, just below border)
            ax.text(v, 0.88, str(v), ha='center', va='top',
                    fontsize=9, color=COLORS['navy'], fontname='Ginto Normal Light')

        # --- X-axis column headers (top, outside grid) ---
        for pos, label in [(1.67, 'Low Standards'), (3.00, 'Medium Standards'), (4.33, 'High Standards')]:
            ax.text(pos,5.45, label, ha='center', va='bottom',
                    fontsize=11, color=COLORS['navy'], fontweight='bold',
                    fontname='Ginto Normal Medium')

        # --- Y-axis row headers (left, fully outside grid) ---
        for pos, label in [(4.33, 'High Psychological\nSafety'),
                           (3.00, 'Medium\nPsychological Safety'),
                           (1.67, 'Low Psychological\nSafety')]:
            ax.text(0.05, pos, label, ha='center', va='center',
                    fontsize=9, color=COLORS['navy'], fontweight='bold',
                    fontname='Ginto Normal Medium')

        # --- Attribution text below chart ---
        ax.text(3.0, 0.42, 'Adapted from Amy Edmonson, ',
                ha='right', va='top', fontsize=7, color=COLORS['dark_gray'],
                fontname='Ginto Normal Light')
        ax.text(3.0, 0.42, 'The Fearless Organization',
                ha='left', va='top', fontsize=7, color=COLORS['dark_gray'],
                fontstyle='italic', fontname='Ginto Normal Light')

        # --- Axis limits and cleanup ---
        ax.set_xlim(-0.7, 6.72)
        ax.set_ylim(0.5, 5.4)

        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
        for spine in ax.spines.values():
            spine.set_visible(False)

        fig.subplots_adjust(left=0.01, right=0.99, top=0.90, bottom=0.08)

        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches=None,
                    facecolor='#F7F5F2', edgecolor='none')
        buf.seek(0)
        plt.close(fig)
        return buf
