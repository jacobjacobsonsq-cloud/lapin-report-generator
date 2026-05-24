# ===================================================================================
# FILE 2: src/chart_generator.py
# ===================================================================================

import matplotlib
matplotlib.use('Agg', force=True)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from io import BytesIO
import pandas as pd
import textwrap

# Lapin Brand Colors (Exact from brand guide)
COLORS = {
    'navy': '#1A1A42',           # R26 G26 B66 - Main dark
    'blue': '#3C78E6',           # R60 G120 B230 - Main accent  
    'light_gray': '#D0D3D6',     # R208 G211 B214
    'ivory': '#F7F5F2',          # R247 G245 B242
    'light_navy': '#33337F',     # R51 G51 B127
    'light_blue': '#828CF9',     # R130 G140 B249 (corrected from 82AAF9)
    'dark_gray': '#8B9197'       # R139 G145 B151 //use for dist bar grap
    #remove the dashed greye lknie for dist graph
}

class ChartGenerator:
    """Generates all chart types with Lapin branding"""
    
    
    def __init__(self, processor):
        self.processor = processor
    
        # Register Ginto font with matplotlib
        import matplotlib.font_manager as fm
        import os
    
        # Path to font file
        font_medium = os.path.join('assets', 'fonts', 'ginto-normal-medium.otf')
        font_light = os.path.join('assets', 'fonts', 'ginto-normal-light.otf')
        font_bold = os.path.join('assets', 'fonts', 'ginto-normal-bold.otf')

        # Add font if it exists
        if os.path.exists(font_medium):
            fm.fontManager.addfont(font_medium)
            print("✓ Ginto Normal Medium font loaded")
        if os.path.exists(font_light):
            fm.fontManager.addfont(font_light)
            print("✓ Ginto Normal Light font loaded")
        if os.path.exists(font_bold):
            fm.fontManager.addfont(font_bold)
            print("✓ Ginto Normal Bold font loaded")
        else:
            print("⚠ Ginto font not found, using default Arial")
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica']
    
    def _save_chart_to_bytes(self, fig, tight=True):
        """Save matplotlib figure to bytes for PowerPoint"""
        buf = BytesIO()
        bbox = 'tight' if tight else None
        fig.savefig(buf, format='png', dpi=150, bbox_inches=bbox,
                   facecolor=COLORS['ivory'], edgecolor='none')
        buf.seek(0)
        plt.close(fig)
        return buf
    
    def _truncate_label(self, text, max_len=35):
        """Truncate long text labels"""
        return text[:max_len] + '...' if len(text) > max_len else text
    
    def _apply_light_font_to_axes(self, ax):
        """Apply Ginto Normal Light and Lapin Navy to all axis labels"""
        for label in ax.get_xticklabels():
            label.set_fontname('Ginto Normal Light')
            label.set_color(COLORS['navy'])
        for label in ax.get_yticklabels():
            label.set_fontname('Ginto Normal Light')
            label.set_color(COLORS['navy'])

    def create_stacked_bar(self, questions, role=None):
        """Stacked bar chart (Disagree/Neutral/Agree) - FIXED FORMATTING"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Calculate distributions
        disagree_vals = []
        neutral_vals = []
        agree_vals = []
        
        for q in questions:
            dist = self.processor.calculate_distribution(q, role)
            disagree_vals.append(dist['disagree'])
            neutral_vals.append(dist['neutral'])
            agree_vals.append(dist['agree'])

        # Create THINNER stacked bars (width 0.4 instead of 0.5)
        x = np.arange(len(questions))
        width = 0.4
        
        ax.set_facecolor(COLORS['ivory'])
        p1 = ax.bar(x, disagree_vals, width, label='Disagree', color=COLORS['dark_gray'])
        p2 = ax.bar(x, neutral_vals, width, bottom=disagree_vals, 
                   label='Neutral', color=COLORS['blue'])
        p3 = ax.bar(x, agree_vals, width, 
                   bottom=np.array(disagree_vals) + np.array(neutral_vals), 
                   label='Agree', color=COLORS['navy'])
        
        # Percentage labels — show all non-zero values; smaller font for tiny segments
        for i, (d, n, a) in enumerate(zip(disagree_vals, neutral_vals, agree_vals)):
            if d > 0:
                fs = 11 if d < 8 else 15
                ax.text(i, d/2, f'{int(d)}%', ha='center', va='center',
                       color='white', fontsize=fs, fontname='Ginto Normal Bold')
            if n > 0:
                fs = 11 if n < 8 else 15
                ax.text(i, d + n/2, f'{int(n)}%', ha='center', va='center',
                       color='white', fontsize=fs, fontname='Ginto Normal Bold')
            if a > 0:
                fs = 11 if a < 8 else 15
                ax.text(i, d + n + a/2, f'{int(a)}%', ha='center', va='center',
                       color='white', fontsize=fs, fontname='Ginto Normal Bold')
        
        # Y-axis: NO LINE, just labels
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 10,20,30,40,50,60,70,80,90,100])
        ax.set_yticklabels(['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'], fontsize=11, color=COLORS['navy'])
        ax.spines['left'].set_visible(False)

        ax.set_xticks(x)
        import textwrap
        wrapped_labels = ['\n'.join(textwrap.wrap(q, 18)) for q in questions]
        ax.set_xticklabels(wrapped_labels, fontsize=11, color=COLORS['navy'], fontweight='normal')

        # Legend at BOTTOM, horizontal, SQUARE markers — lowered to clear multi-line labels
        handles = [mpatches.Rectangle((0,0),1,1, facecolor=COLORS['dark_gray']),
                    mpatches.Rectangle((0,0),1,1, facecolor=COLORS['blue']),
                    mpatches.Rectangle((0,0),1,1, facecolor=COLORS['navy'])]
        legend = ax.legend(handles, ['Disagree', 'Neutral', 'Agree'],
              loc='lower center', bbox_to_anchor=(0.5, -0.38),
              ncol=3, frameon=False, fontsize=11,
              handlelength=1, handleheight=1)
        for text in legend.get_texts():
            text.set_fontweight('normal')
        
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        
        self._apply_light_font_to_axes(ax)
        plt.tight_layout()
        return self._save_chart_to_bytes(fig)
    
    def create_multi_line(self, questions, category=None):
        """Multi-line chart comparing roles (% Agree)"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.set_facecolor(COLORS['ivory'])
        # Use exact brand colors for lines (darkest = navy on top)
        role_colors = [COLORS['dark_gray'], COLORS['blue'], COLORS['navy']]
        
        for i, role in enumerate(reversed(self.processor.roles)):
            percent_agree = self.processor.calculate_percent_agree(questions, role)
            values = [percent_agree.get(q, 0) for q in questions]
            
            ax.plot(range(len(questions)), values, marker='o', linewidth=2,
                   markersize=4, color=role_colors[i % len(role_colors)], 
                   label=f'{role} Agree')
        
        ax.set_ylim(0, 105)
        ax.set_yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        ax.set_yticklabels(['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'], fontsize=11, color=COLORS['navy'])
        ax.spines['left'].set_visible(False)

        ax.set_xticks(range(len(questions)))
        import textwrap
        wrapped_labels = ['\n'.join(textwrap.wrap(q, 18)) for q in questions]
        ax.set_xticklabels(wrapped_labels, fontsize=11, color=COLORS['navy'])

        # Legend at bottom center — lowered to clear multi-line labels
        ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.30),
                 ncol=3, frameon=False, fontsize=11)
        
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        
        self._apply_light_font_to_axes(ax)
        plt.tight_layout()
        return self._save_chart_to_bytes(fig)
    
    def create_average_bars(self, questions, role=None):
        """Simple bar chart showing averages"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.set_facecolor(COLORS['ivory'])
        averages = self.processor.calculate_averages(questions, role)
        values = [averages.get(q, 0) for q in questions]

        bars = ax.bar(range(len(questions)), values, width=0.5, color=COLORS['light_navy'])
        
        # Value labels on bars
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height/2,
                   f'{val:.1f}', ha='center', va='center', 
                   color='white', fontsize=14, fontname='Ginto Normal Bold')

        ax.set_ylim(0, 5.5)
        ax.set_yticks([0, 1, 2, 3, 4, 5])
        ax.spines['left'].set_visible(False)
        
        ax.set_xticks(range(len(questions)))
        import textwrap
        wrapped_labels = ['\n'.join(textwrap.wrap(q, 18)) for q in questions]
        ax.set_xticklabels(wrapped_labels, fontsize=11, color=COLORS['navy'])

        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)

        self._apply_light_font_to_axes(ax)
        plt.tight_layout()
        return self._save_chart_to_bytes(fig)

    def create_single_line(self, questions, role):
        """Single line chart for one role (% Agree)"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.set_facecolor(COLORS['ivory'])
        percent_agree = self.processor.calculate_percent_agree(questions, role)
        values = [percent_agree.get(q, 0) for q in questions]

        ax.plot(range(len(questions)), values, marker='o', linewidth=2,
               markersize=4, color=COLORS['navy'], label=f'{role} Agree')

        ax.set_ylim(0, 105)
        ax.set_yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        ax.set_yticklabels(['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'], fontsize=11, color=COLORS['navy'])
        ax.spines['left'].set_visible(False)

        ax.set_xticks(range(len(questions)))
        import textwrap
        wrapped_labels = ['\n'.join(textwrap.wrap(q, 18)) for q in questions]
        ax.set_xticklabels(wrapped_labels, fontsize=11, color=COLORS['navy'])

        ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.30), frameon=False, fontsize=11)
        
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        
        self._apply_light_font_to_axes(ax)
        plt.tight_layout()
        return self._save_chart_to_bytes(fig)
    
    def create_scatter_plot(self, role=None):
        """9-quadrant scatter plot (High Performing Teams matrix)"""
        fig, ax = plt.subplots(figsize=(7, 5))
        fig.patch.set_facecolor(COLORS['ivory'])
        ax.set_facecolor(COLORS['ivory'])
        
        # Hardcoded question mappings
        standards_questions = [
            "We have a can-do attitude.",
            "We are results driven.",
            "We have high performance expectations in this company.",
            "We effectively address poor performance.",
            "We recognize strong performance."
        ]
        
        psych_safety_questions = [
            "We speak honestly to each other.",
            "Office politics do not influence behavior.",
            "We willingly accept tough feedback.",
            "We encourage differing viewpoints.",
            "It is safe to speak our minds even when our views could be controversial.",
            "We give each other the benefit of the doubt."
        ]
        
        # Get data for this role
        if role:
            data = self.processor.responses[self.processor.responses['Role'] == role].copy()
        else:
            data = self.processor.responses.copy()
        
        # Calculate averages for each person
        x_vals = []
        y_vals = []
        
        for _, row in data.iterrows():
            # Calculate X (Standards average)
            standards_scores = []
            for q in standards_questions:
                if q in data.columns:
                    score = pd.to_numeric(row[q], errors='coerce')
                    if pd.notna(score):
                        standards_scores.append(score)
            
            # Calculate Y (Psychological Safety average)
            psych_scores = []
            for q in psych_safety_questions:
                if q in data.columns:
                    score = pd.to_numeric(row[q], errors='coerce')
                    if pd.notna(score):
                        psych_scores.append(score)
            
            # Only plot if we have data for both
            if standards_scores and psych_scores:
                x_vals.append(np.mean(standards_scores))
                y_vals.append(np.mean(psych_scores))
        
        # Background shading
        ax.axhspan(1, 5, facecolor=COLORS['ivory'], alpha=1, zorder=0)
        
        # Add zone division lines (ONLY within grid, not through border)
        ax.plot([1, 5], [3.67, 3.67], color=COLORS['navy'], linewidth=2, alpha=0.8, zorder=1)
        ax.plot([1, 5], [2.33, 2.33], color=COLORS['navy'], linewidth=2, alpha=0.8, zorder=1)
        ax.plot([2.33, 2.33], [1, 5], color=COLORS['navy'], linewidth=2, alpha=0.8, zorder=1)
        ax.plot([3.67, 3.67], [1, 5], color=COLORS['navy'], linewidth=2, alpha=0.8, zorder=1)

        # Plot the scatter points (smaller, darker)
        if x_vals and y_vals:
            ax.scatter(x_vals, y_vals, s=40, alpha=0.95, color=COLORS['navy'], 
                    edgecolors=COLORS['navy'], linewidth=0.5, zorder=2)
        
        # Zone labels (NOT italicized, bigger, dark gray)
        ax.text(1.67, 4.33, 'Complacent\nZone', ha='center', va='center', 
            fontsize=13, alpha=0.5, color=COLORS['dark_gray'])
        ax.text(3, 4.33, 'Learning\nZone', ha='center', va='center', 
            fontsize=13, alpha=0.5, color=COLORS['dark_gray'])
        ax.text(4.33, 4.33, 'Excellence\nZone', ha='center', va='center', 
            fontsize=13, alpha=0.5, color=COLORS['dark_gray'])
        
        ax.text(1.67, 3, 'Apathy\nZone', ha='center', va='center', 
            fontsize=13, alpha=0.5, color=COLORS['dark_gray'])
        ax.text(3, 3, 'Comfort\nZone', ha='center', va='center', 
            fontsize=13, alpha=0.5, color=COLORS['dark_gray'])
        ax.text(4.33, 3, 'Performance\nZone', ha='center', va='center', 
            fontsize=13, alpha=0.5, color=COLORS['dark_gray'])
        
        ax.text(1.67, 1.67, 'Frozen\nZone', ha='center', va='center', 
            fontsize=13, alpha=0.5, color=COLORS['dark_gray'])
        ax.text(3, 1.67, 'Insecurity\nZone', ha='center', va='center', 
            fontsize=13, alpha=0.5, color=COLORS['dark_gray'])
        ax.text(4.33, 1.67, 'Anxiety\nZone', ha='center', va='center', 
            fontsize=13, alpha=0.5, color=COLORS['dark_gray'])
        
        # X-axis labels (TOP, Ginto Normal Medium, larger, navy, bold)
        ax.text(1.67, 5.25, 'Low Standards', ha='center', va='bottom', 
            fontsize=13, color=COLORS['navy'], fontweight='bold', fontname='Ginto Normal Medium')
        ax.text(3, 5.25, 'Medium Standards', ha='center', va='bottom', 
            fontsize=13, color=COLORS['navy'], fontweight='bold', fontname='Ginto Normal Medium')
        ax.text(4.33, 5.25, 'High Standards', ha='center', va='bottom', 
            fontsize=13, color=COLORS['navy'], fontweight='bold', fontname='Ginto Normal Medium')
        
        # Y-axis labels (LEFT, centered, Ginto Normal Medium, larger, navy, bold)
        ax.text(0.7, 4.33, 'High\nPsychological\nSafety', ha='center', va='center', 
            fontsize=12, color=COLORS['navy'], fontweight='bold', fontname='Ginto Normal Medium')
        ax.text(0.7, 3, 'Medium\nPsychological\nSafety', ha='center', va='center', 
            fontsize=12, color=COLORS['navy'], fontweight='bold', fontname='Ginto Normal Medium')
        ax.text(0.7, 1.67, 'Low\nPsychological\nSafety', ha='center', va='center', 
            fontsize=12, color=COLORS['navy'], fontweight='bold', fontname='Ginto Normal Medium')
        
        # Set limits with border padding
        ax.set_xlim(0.6, 5.3)
        ax.set_ylim(0.8, 5.5)
        
        # Remove ticks and spines
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
        
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        plt.tight_layout()
        return self._save_chart_to_bytes(fig, tight=False)
