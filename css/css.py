import re


def extract_color_values(color_string):
    """
    Extracts color values from a color string.

    Args:
        color_string (str): The color string to extract values from.

    Returns:
        dict or None: A dictionary containing the extracted color values, 
        or None if the color string does not match the expected format.

    Examples:
        >>> extract_color_values('hsl(240, 100%, 50%)')
        {'h': '240', 's': '100%', 'l': '50%'}

        >>> extract_color_values('rgb(255, 0, 0)')
        {'r': '255', 'g': '0', 'b': '0'}

        >>> extract_color_values('invalid_color')
        None
    """
    hsl_match = re.match(r'hsl\((\d+),\s*(\d+%)?,\s*(\d+%)?\)', color_string)
    rgb_match = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', color_string)

    if hsl_match:
        h, s, l = hsl_match.groups()
        return {'h': h, 's': s, 'l': l}
    elif rgb_match:
        r, g, b = rgb_match.groups()
        return {'r': r, 'g': g, 'b': b}
    return None


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


def generate_css(variables: dict) -> dict:
    """Generates the CSS from the given variables.

    Args:
        variables (dict): The dictionary of variables to generate CSS from.

    Returns:
        dict: The resulting map of root selectors, to states, to the CSS variables and their values.
    """
    variables_map = {}
    extract_variables(variables['variables'],
                      variables_map, "", variables['modes'])
    return variables_map


def is_state(key: str) -> bool:
    """Checks if the key is a state. A state is a key that is either default, hover, focus, active, or disabled.

    Args:
        key (str): The key to check if it is a state.

    Returns:
        bool: Whether or not the key is a state.
    """
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
            # Set the state to true and reset the key
            # Make sure only one state is true, otherwise it will all default to is_hover
            lowered_key = key.lower()
            if lowered_key == "hover":
                is_hover = True
                is_active = False
                is_focus = False
                is_disabled = False
            elif lowered_key == "focus":
                is_focus = True
                is_hover = False
                is_active = False
                is_disabled = False
            elif lowered_key == "active":
                is_active = True
                is_hover = False
                is_focus = False
                is_disabled = False
            elif lowered_key == "disabled":
                is_disabled = True
                is_hover = False
                is_focus = False
                is_active = False
            key = ""

        if key != "":
            new_current_var = f"{current_var}-{key}" if current_var else key
        else:
            new_current_var = current_var

        if 'values' in value:
            for mode in modes:
                mode_key = f":root[data-mode='{mode}']" if len(
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

                if is_alias(str(css_var_value)):
                    css_var_value = f"var(--{convert_alias_to_css(css_var_value)})"
                elif extract_color_values(str(css_var_value)):
                    color_values = extract_color_values(css_var_value)
                    if 'h' in color_values:
                        css_var_value = f"{color_values['h']}deg {color_values['s']} {color_values['l']}"
                    elif 'r' in color_values:
                        css_var_value = f"{color_values['r']} {color_values['g']} {color_values['b']}"

                if css_var_name not in variables_map[mode_key][state_key]:
                    variables_map[mode_key][state_key][css_var_name] = css_var_value
                else:
                    print(f"Duplicate variable found: {css_var_name}")

        else:
            extract_variables(value, variables_map, new_current_var,
                              modes, is_hover, is_focus, is_active, is_disabled)
