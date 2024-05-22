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
    
    def process_variables(var_dict: dict, path=""):
        nonlocal css_content
        for key, value in var_dict.items():
            current_path = f"{path}-{key}" if path else key
            if isinstance(value, dict) and 'values' in value:
                for mode, mode_value in value['values'].items():
                    css_var = f"{prefix}-{current_path.lower()}"
                    css_content += f"\t{css_var}: {mode_value};\n"
            elif isinstance(value, dict):
                process_variables(value, current_path)
            
    for collection in variables['collections']:
        modes: list[str] = collection['modes']
        if len(modes) == 1:
            css_content += f":root {{\n"
            process_variables(collection['variables'])
            css_content += "}\n"
        else:
            for mode in modes:
                css_content += f"[data-theme=\"{mode}\"] {{\n"
                process_variables(collection['variables'])
                css_content += "}\n\n"
    
    return css_content