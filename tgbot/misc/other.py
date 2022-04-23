def get_full_city_name(el: dict, sep: str = ", "):
    country = "Беларусь" if el['country'] == "Белоруссия" else el['country']
    return f"{el['city']}{sep}{el['region']}{sep}{country}"


def format_name(name: str):
    if not name:
        return "???"
    return "@" + name
