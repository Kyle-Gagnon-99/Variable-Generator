import argparse
import logging
import os

from utils.generator_logging import setup_logging
from utils.generator_toml import load_config
from utils.generator_json import load_json
from css.css import generate_css


def parse_args():
    """Parses the arguments for the script."""
    arg_parser = argparse.ArgumentParser(
        description="Generates CSS from JSON files.")
    arg_parser.add_argument(
        "-c", "--config", help="The path to the config file.", type=str, default="config.toml")
    arg_parser.add_argument(
        "-d", "--dry-run", help="Runs the script without saving the CSS.", action="store_true")
    arg_parser.add_argument(
        "-r", "--remove", help="Removes the CSS file if it exists.", action="store_true", default=True)

    # Parse the arguments
    args = arg_parser.parse_args()
    return args


def rmeove_file(output_dir: str, file_name: str) -> None:
    """Removes the file if it exists.

    Args:
        output_dir (str): The directory of the file.
        file_name (str): The name of the file.
    """
    if os.path.exists(f"{output_dir}/{file_name}"):
        os.remove(f"{output_dir}/{file_name}")
        logging.info(f"Removed {output_dir}/{file_name}")


def save_file(content: dict, output_dir: str, file_name: str, is_tailwind: bool) -> None:
    """Saves the content to a file.

    Args:
        content (str): The content to save.
        output_dir (str): The directory to save the file in.
        file_name (str): The name of the file.
    """
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/{file_name}", 'a') as file:
        # If this is a Tailwind CSS file, then add the Tailwind CSS imports
        if is_tailwind:
            file.write("@tailwind base;\n")
            file.write("@tailwind components;\n")
            file.write("@tailwind utilities;\n\n")

            file.write("@layer base {\n")

        # Loop through the content and write it to the file
        # The top level is the :root or :root[data-theme="theme-name"]
        # Then the next level is :root[state] or :root[data-theme="theme-name"]:[state] if the state is not default
        # Then the next level is the variable name and the value
        for key, value in content.items():
            for state, variables in value.items():
                state_modifier = f":{state}" if state != "default" else ""
                file.write(f"\t{key}{state_modifier} {{\n") if is_tailwind else file.write(
                    f"{key}{state_modifier} {{\n")
                for variable, value in variables.items():
                    file.write(f"\t\t--{variable}: {value};\n")
                file.write("\t}\n\n")

        if is_tailwind:
            file.write("}\n")

    logging.info(f"Saved CSS to {output_dir}/{file_name}")


def main():
    args = parse_args()

    config = load_config(args.config if args.config else "config.toml")

    setup_logging(config['logging']['level'])
    logging.debug("Logging is setup.")
    logging.info("Starting the generator.")

    # Input directory
    input_dir = config['settings']['input_dir']

    # Output directory and file
    output_dir = config['css']['output']['dir']
    file_name = config['css']['output']['file']

    # Remove the file if it exists, if the remove flag is set
    if args.remove:
        rmeove_file(output_dir, file_name)

    # The map of all variables
    all_variables = {}

    # Loop through each input file
    for input_file in config['settings']['input_files']:
        logging.info(f"Loading {input_file}...")
        variables = load_json(f"{input_dir}/{input_file}")

        # Inside each input file, there is a list of collections, so loop through the collections
        for collection in variables['collections']:
            logging.info(f"Generating CSS for {collection['name']}...")
            variables_map = generate_css(collection)

            # Update the all_variables dictionary with the variables_map by merging the dictionaries at the state level
            for key, value in variables_map.items():
                if key in all_variables:
                    for state, variables in value.items():
                        if state in all_variables[key]:
                            all_variables[key][state].update(variables)
                        else:
                            all_variables[key][state] = variables
                else:
                    all_variables[key] = value

    logging.debug(all_variables)

    # Write the CSS to a file

    save_file(all_variables, output_dir, file_name,
              config['css']['tailwindcss'])


if __name__ == '__main__':
    main()
