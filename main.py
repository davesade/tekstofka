import os
import sys
import yaml
from flatten_dict import flatten
from flatten_dict import unflatten
from time import sleep


class skip(Exception):
    pass


def load_data(filename):
    gamefile = open(filename, "r", encoding="utf-8")
    data = yaml.safe_load(gamefile)
    return data


def victory(game_state):
    print(game_state["victory_text"])
    os._exit(0)


def load_additional_descriptions(room):
    additional_descriptions = []
    try:
        for additional_description in room["moznosti"]:
            if room["moznosti"][additional_description]["visible"]:
                additional_descriptions.append(
                    room["moznosti"][additional_description]["popis"]
                )
    finally:
        return additional_descriptions


def load_exits(room):
    exits = []
    try:
        for exit in room["vychody"]:
            if room["vychody"][exit]["visible"]:
                exits.append(exit)
    finally:
        return exits


def load_options(room):
    options = {}
    try:
        for option in room["moznosti"]:
            if room["moznosti"][option]["visible"]:
                options.update({option: room["moznosti"][option]})
    finally:
        return options


def update_game_state(game_state):
    active_room_id = game_state["active_room_id"]
    active_room = game_state[active_room_id]
    additional_descriptions = load_additional_descriptions(active_room)
    exits = load_exits(active_room)
    options = load_options(active_room)

    print(active_room["popis"])
    print(" ".join(additional_descriptions))
    print("Mozne vychody: ", " ".join(exits))

    command = input()
    print("###################")

    updated_game_state = execute_command(
        command, options, exits, active_room_id, game_state
    )

    return updated_game_state


def execute_command(command, options, exits, active_room_id, game_state):
    # special commands
    # save, load, exit, help

    try:
        words = command.split(" ")
        for i, word in enumerate(words):
            if len(word) < 3:
                words.pop(i)
        if words[0] in exits:
            print(game_state[active_room_id]["vychody"][words[0]]["popis"])
            game_state["active_room_id"] = game_state[active_room_id]["vychody"][
                words[0]
            ]["target"]
            raise (skip)

        for option in options:
            if (
                words[0] in options[option]["actions"]
                and words[1] in options[option]["keywords"]
            ):
                print(options[option]["reakce"])
                flat_game_state = flatten(game_state)
                flat_update = {}
                if "targets" in options[option]:
                    flat_update = flatten(options[option]["targets"])
                updated_game_state = unflatten(flat_game_state | flat_update)
                game_state = updated_game_state
                raise (skip)

        print("Bohuzel jsem nerozeznal prikaz...")
        sleep(3)

    finally:
        return game_state


if __name__ == "__main__":
    initial_data_file_name = "data.yaml"
    game_state = load_data(initial_data_file_name)
    print(game_state["intro_text"])

    while game_state["victory"] != True:
        game_state = update_game_state(game_state)

    victory(game_state)
