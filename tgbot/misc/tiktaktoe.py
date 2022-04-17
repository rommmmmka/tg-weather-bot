import random

TIKTAKTOE_EMOJI = {
    "Cross": "\u274C",
    "Zero": "\u2B55",
    "Empty": "\u2B1C",
}


def get_tiktaktoe_patterns():
    patterns = [[[0, 0, 0], [0, 0, 0], [0, 0, 0]] for _ in range(8)]
    for i in range(3):
        for j in range(3):
            patterns[i][i][j] = 1
            patterns[i + 3][j][i] = 1
        patterns[6][i][i] = 1
        patterns[7][2 - i][i] = 1
    return patterns


def tiktaktoe_check_win(kb):
    patterns = get_tiktaktoe_patterns()
    for player in [TIKTAKTOE_EMOJI['Cross'], TIKTAKTOE_EMOJI['Zero']]:
        for pattern in patterns:
            win = True
            for i in range(3):
                for j in range(3):
                    if pattern[i][j] == 0:
                        continue
                    if kb[i][j]['text'] != player:
                        win = False
                        break
                if not win:
                    break
            if win:
                return player
    for i in range(3):
        for j in range(3):
            if kb[i][j]['text'] == TIKTAKTOE_EMOJI['Empty']:
                return 0
    return -1


def tiktaktoe_place_zero(kb):
    patterns = get_tiktaktoe_patterns()
    random.shuffle(patterns)
    place_coords = [[-1, -1], [-1, -1], [-1, -1], [-1, -1]]

    base_place_coords = []
    for i in range(3):
        for j in range(3):
            if kb[i][j]['text'] == TIKTAKTOE_EMOJI['Empty']:
                base_place_coords.append([i, j])
    if not base_place_coords:
        base_place_coords.append([-1, -1])
    place_coords.append(random.choice(base_place_coords))

    for pattern in patterns:
        can_place = True
        curr_place_coords = []
        for i in range(3):
            for j in range(3):
                if pattern[i][j] == 0:
                    continue
                if kb[i][j]['text'] == TIKTAKTOE_EMOJI['Cross']:
                    can_place = False
                    break
                if kb[i][j]['text'] == TIKTAKTOE_EMOJI['Empty']:
                    curr_place_coords.append([i, j])
            if not can_place:
                break
        if can_place:
            curr_choice = random.choice(curr_place_coords)
            place_coords[len(curr_place_coords)] = curr_choice

    for pattern in patterns:
        need_to_place = True
        curr_place_coords = []
        for i in range(3):
            for j in range(3):
                if pattern[i][j] == 0:
                    continue
                if kb[i][j]['text'] == TIKTAKTOE_EMOJI['Zero']:
                    need_to_place = False
                    break
                if kb[i][j]['text'] == TIKTAKTOE_EMOJI['Empty']:
                    curr_place_coords.append([i, j])
            if not need_to_place:
                break
        if need_to_place and len(curr_place_coords) == 1:
            place_coords[0] = curr_place_coords[0]

    place_coords[0], place_coords[1] = place_coords[1], place_coords[0]
    for coords in place_coords:
        if coords == [-1, -1]:
            continue
        kb[coords[0]][coords[1]]['text'] = TIKTAKTOE_EMOJI['Zero']
        break
    return kb


def tiktaktoe_kill_callback_queries(kb):
    for i in range(3):
        for j in range(3):
            kb['inline_keyboard'][i][j]['callback_data'] = "killed_callback_query"
    return kb
