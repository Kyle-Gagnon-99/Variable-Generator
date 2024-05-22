import re


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


def generate_css(variables: dict, config: dict) -> str:
    """Generates CSS from the variables and config.

    Args:
        variables (dict): The variables to generate CSS from.
        config (dict): The configuration to use.

    Returns:
        str: The resulting CSS.
    """
    css_content = ""
    prefix = config["css"]["prefix"]

    def process_variables(mode: str, var_dict: dict, path=""):
        nonlocal css_content
        for key, value in var_dict.items():
            current_path = f"{path}-{key}" if path else key
            if isinstance(value, dict) and 'values' in value:
                mode_value = value['values'].get(mode)
                if prefix != "":
                    css_var = f"--{prefix}-{current_path}"
                else:
                    css_var = f"--{current_path}"
                # If mode_value is an alias, convert it to CSS variable
                if isinstance(mode_value, str) and is_alias(mode_value):
                    if prefix != "":
                        css_content += f"\t{css_var}: var(--{prefix}-{convert_alias_to_css(mode_value)});\n"
                    else:
                        css_content += f"\t{css_var}: var(--{convert_alias_to_css(mode_value)});\n"
                else:
                    css_content += f"\t{css_var}: {mode_value};\n"
            elif isinstance(value, dict):
                process_variables(mode, value, current_path)

    for collection in variables['collections']:
        modes: list[str] = collection['modes']
        if len(modes) == 1:
            css_content += f":root {{\n"
            process_variables(modes[0], collection['variables'])
            css_content += "}\n"
        else:
            for mode in modes:
                css_content += f"[data-theme=\"{mode}\"] {{\n"
                process_variables(mode, collection['variables'])
                css_content += "}\n\n"

    return css_content
