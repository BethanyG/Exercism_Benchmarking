import timeit
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import matplotlib.axes as maxis
import seaborn as sns
from matplotlib.colors import ListedColormap



# Data and timing/timeit setup
loops = 1_000_000

row_headers = ["if-statements", "ternary", "datetime-add", "calendar-isleap"]
col_headers = ["1900", "2000", "2019", "2020"]

# empty dataframe will be filled in one cell at a time later
df = pd.DataFrame(np.nan, index=row_headers, columns=col_headers)

setups = {}

setups["if-statements"] = """
def leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
"""

setups["ternary"] = """
def leap_year(year):
    return not year % 400 if not year % 100 else not year % 4
"""

setups["datetime-add"] = """
from datetime import datetime, timedelta

def leap_year(year):
    return (datetime(year, 2, 28) + timedelta(days=1)).day == 29
"""

setups["calendar-isleap"] = """
from calendar import isleap

def leap_year(year):
    return isleap(year)
"""

for descriptor in row_headers:
    val = timeit.timeit("""leap_year(1900)""", setups[descriptor], number=loops) / loops
    year = '1900'
    print(f"{descriptor} {year}: {val}")
    df.loc[descriptor, year] = val

    val = timeit.timeit("""leap_year(2000)""", setups[descriptor], number=loops) / loops
    year = '2000'
    print(f"{descriptor} {year}: {val}")
    df.loc[descriptor, year] = val

    val = timeit.timeit("""leap_year(2019)""", setups[descriptor], number=loops) / loops
    year = '2019'
    print(f"{descriptor} {year}: {val}")
    df.loc[descriptor, year] = val

    val = timeit.timeit("""leap_year(2020)""", setups[descriptor], number=loops) / loops
    year = '2020'
    print(f"{descriptor} {year}: {val}")
    df.loc[descriptor, year] = val



# Classes for rounded figure border
class StaticColorAxisBBox(mpatches.FancyBboxPatch):
    def set_edgecolor(self, color):
        if hasattr(self, "_original_edgecolor"):
            return
        self._original_edgecolor = color
        self._set_edgecolor(color)

    def set_linewidth(self, w):
        super().set_linewidth(1.5)


class FancyAxes(maxis.Axes):

    def __init__(self, *args, **kwargs):
        self._edgecolor = kwargs.pop("edgecolor", 'white')
        super().__init__(*args, **kwargs)

    def _gen_axes_patch(self):
        return StaticColorAxisBBox(
            (0, 0),
            1.0,
            1.0,
            boxstyle="round, rounding_size=0.06, pad=.01",
            edgecolor='white',
            linewidth=8,
        )



base_color = 'white'
palette_colors = ["#AFAD6A", "#B1C9FD", "#CDC6FD", "#FABD19", "#3B76F2",
                  "#7467D1", "#FA9A19", "#85832F", "#1A54CE","#4536B0"]

my_cmap = ListedColormap(sns.color_palette(palette_colors, as_cmap=True))


mpl.rcParams['text.color'] = base_color
mpl.rcParams['axes.labelcolor'] = base_color
mpl.rcParams['xtick.color'] = base_color
mpl.rcParams['ytick.color'] = base_color
mpl.rcParams['lines.color'] = base_color
mpl.rcParams['axes.spines.left'] = False
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['axes.spines.top'] = False
mpl.rcParams['axes.spines.bottom'] = False
mpl.rcParams['axes.facecolor'] = 'none'
mpl.rcParams["axes.axisbelow"] = "line"
mpl.rcParams["font.family"] = 'Poppins'



# Bar plot of actual run times
fig, ax2 = plt.subplots(facecolor="none", subplot_kw={'axes_class': FancyAxes, 'edgecolor': base_color})
ax2.set_clip_on(True)

ax2= df.plot.bar(figsize=(18, 12),
            ax=ax2,
            fontsize=24,
            width=0.89,
            rot=0,
            colormap=my_cmap,
            alpha=0.9,
            linewidth=0,
            legend=False)


# Set gridlines and hide "noisy" gridlines
ax2.grid(axis='y', linestyle=':', lw=2.0, color=base_color, zorder=0)

# Turn off x gridlines
ax2.grid(axis='x', color="none")


gridlines = ax2.get_ygridlines()[::-1]
for grid in gridlines:
    grid.set_visible(False)

gridlines[-3].set_visible(True)
gridlines[-2].set_visible(True)
gridlines[1].set_visible(True)


# Set and format axis labels and ticks
# This is the parameter for the 1e-7 notation on the yaxis
ax2.yaxis.offsetText.set_visible(True)

# Y axis ticks and tick lable formatting
ax2.tick_params(axis="y", direction="in", pad=-25)
plt.ticklabel_format(axis='y', style='sci', scilimits=(2,1), useOffset=False, useMathText=True)
plt.setp(ax2.get_yticklabels(), weight='heavy', color=base_color, zorder=1)

plt.setp(ax2.get_yticklabels()[0], visible=False)
plt.setp(ax2.get_yticklabels()[-1], visible=False)


# X axis ticks and tick lable formatting
ax2.tick_params(axis="x", direction="in", pad=-25, zorder=1)

# Due to WCAG, this needs to stay white and not change with the background.
plt.setp(ax2.get_xticklabels(), weight='bold', color='white', zorder=1)



# Set the bar labels instead of using legend (WCAG suggestion)
for number, container in enumerate(ax2.containers):
    labels = [f'{col_headers[number]}' for item in range(4)]
    ax2.bar_label(ax2.containers[number], labels=labels, label_type='edge', color=base_color, size=20, padding=4)



# Save out figure as SVG Note the different extension for light vs dark
# Dark version
plt.savefig('../leap_timeit_bar_plot-dark.svg', facecolor=fig.get_facecolor(), transparent=False)

# Light version
#plt.savefig('../leap_timeit_bar_plot-light.svg', facecolor=fig.get_facecolor(), transparent=True)


# The next bit will be useful for `introduction.md`
# pd.options.display.float_format = '{:,.2e}'.format
print('\nDataframe in Markdown format:\n')
print(df.to_markdown(floatfmt=".1e"))