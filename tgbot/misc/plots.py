import math
import random
from io import BytesIO

from matplotlib import pyplot as plt
from seaborn import color_palette

COLOR_PALETTES = ["mako", "rocket", "magma", "viridis"]


def draw_hist(x: list, y: list):
    plt.figure(figsize=(19, 10), dpi=100)
    plt.bar(x, y, color=color_palette(random.choice(COLOR_PALETTES), len(x)), width=.7)
    for i, val in enumerate(y):
        plt.text(i, val, val, horizontalalignment='center', verticalalignment='bottom', weight=500, size=14)

    plt.gca().set_xticks(x)
    plt.gca().set_xticklabels(x, rotation=45, horizontalalignment='right')
    plt.ylabel('Количество запросов', fontsize=16)
    ticks_max = math.ceil(y[0] * 1.2)
    plt.yticks(range(ticks_max + 1))

    img = BytesIO()
    plt.savefig(img, format="png", bbox_inches='tight', pad_inches=0.3)
    plt.close()
    img.seek(0)
    return img


def draw_circle(categories: list, data: list):
    fig, ax = plt.subplots(figsize=(19, 10), subplot_kw=dict(aspect="equal"), dpi=150)

    explode = [0.] * len(data)
    if len(data) > 2:
        explode[random.randint(1, len(data) - 1)] = 0.1

    wedges, texts, autotexts = ax.pie(data, autopct=lambda pct: round(pct / 100. * sum(data)),
                                      textprops=dict(color="w"),
                                      colors=color_palette(random.choice(COLOR_PALETTES), len(data)),
                                      startangle=140, explode=explode)

    ax.legend(wedges, categories, title="Города", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    plt.setp(autotexts, size=15, weight=700)

    img = BytesIO()
    plt.savefig(img, format="png", bbox_inches='tight')
    plt.close()
    img.seek(0)
    return img


def get_plot(plot_type: str, queries: list, cities: list):
    if plot_type in ["hist", "h"]:
        return draw_hist(cities, queries)
    return draw_circle(cities, queries)
