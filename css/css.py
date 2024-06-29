import re
import logging


def is_alias(value: str) -> bool:
    # Check if the value is an alias by checking if it contains a color
    # Example: "colors:primary" -> True
    # Example: "primary" -> False
    # Example: "Collection Name With Spaces:variable-name" -> True
    # Example: "Just a string with a colon in it: It will fail because there is a space before the colon" -> False
    # Example: "Just a string with a colon in it: It will fail because there is a space after the colon " -> False
    return re.search(r"[\w\s]+:[\w\s]+", value) is not None


def convert_alias_to_css(value: str) -> str:
    # Split the alias into collection and variable and only return the variable
    # Example: "colors:primary" -> "primary"
    # Also, convert the variable to kebab-case
    return value.split(":")[1].replace("/", "-")


def generate_css(config: dict, variables: dict):
    variables_map = {}
    extract_variables(variables['variables'],
                      variables_map, "", variables['modes'])
    print(variables_map)
    return variables_map


def is_state(key: str) -> bool:
    # Check to see if it is a state (default, hover, focus, active, disabled)
    # If so return true, otherwise return false
    if key == "default" or key == "hover" or key == "focus" or key == "active" or key == "disabled":
        return True
    else:
        return False


def extract_variables(variables: dict,
                      variables_map: dict,
                      current_var: str,
                      modes: list,
                      is_hover: bool = False,
                      is_focus: bool = False,
                      is_active: bool = False,
                      is_disabled: bool = False):
    """Extracts the variables from the JSON file. It converts the variables into CSS variables.

    Args:
        variables (dict): The variables to extract.
        variables_map (dict): The map of variables to extract. The key is either :root or :root[data-theme="theme-name"] if there is more than one mode. Inside the values is a dictionary of states to the list of CSS variables and their value
        current_var (str): The current variable being built
        modes (list): The list of modes for the collection. Used as the key for the values key.
        is_hover (bool, optional): Whether or not it is a hover state variable (maps to :root:hover). Defaults to False.
        is_focus (bool, optional): Whehter or not it is a focus state variable (maps to :root:focus). Defaults to False.
        is_active (bool, optional): Whehter or not it is an active state variable (maps to :root:active). Defaults to False.
        is_disabled (bool, optional): Whehter or not it is a disabled state variable (maps to :root:disabled). Defaults to False.
    """

    # Loop through the dictionary of variables
    for key, value in variables.items():
        if is_state(key):
            lowered_key = key.lower()
            logging.debug(f"State found: {lowered_key}")
            if lowered_key == "hover":
                is_hover = True
            elif lowered_key == "focus":
                is_focus = True
            elif lowered_key == "active":
                is_active = True
            elif lowered_key == "disabled":
                is_disabled = True
            key = ""

        new_current_var = f"{current_var}-{key}" if current_var else key

        if 'values' in value:
            for mode in modes:
                mode_key = f":root[data-theme='{mode}']" if len(
                    modes) > 1 else ":root"
                if mode_key not in variables_map:
                    variables_map[mode_key] = {}

                state_key = "default"
                if is_hover:
                    state_key = "hover"
                elif is_focus:
                    state_key = "focus"
                elif is_active:
                    state_key = "active"
                elif is_disabled:
                    state_key = "disabled"

                if state_key not in variables_map[mode_key]:
                    variables_map[mode_key][state_key] = {}

                css_var_name = f"--{new_current_var}".strip("-")
                css_var_value = value['values'][mode]

                if is_alias(css_var_value):
                    css_var_value = f"var(--{convert_alias_to_css(css_var_value)})"

                if css_var_name not in variables_map[mode_key][state_key]:
                    variables_map[mode_key][state_key][css_var_name] = css_var_value
                else:
                    print(f"Duplicate variable found: {css_var_name}")

        else:
            extract_variables(value, variables_map, new_current_var,
                              modes, is_hover, is_focus, is_active, is_disabled)
