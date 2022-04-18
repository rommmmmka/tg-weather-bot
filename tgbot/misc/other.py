from io import BytesIO

from matplotlib import pyplot as plt


def get_full_city_name(el: dict, sep: str = ", "):
    country = "Беларусь" if el['country'] == "Белоруссия" else el['country']
    return f"{el['city']}{sep}{el['region']}{sep}{country}"


def draw_hist(x: list, y: list, ticks_max: int):
    plt.rc('xtick', labelsize=6)
    plt.bar(x, y)
    plt.yticks(range(ticks_max + 1))
    plt.subplots_adjust(bottom=0.15)
    img = BytesIO()
    plt.savefig(img, format="png")
    plt.close()
    img.seek(0)
    return img


def format_name(name: str):
    if not name:
        return "???"
    return "@" + name
