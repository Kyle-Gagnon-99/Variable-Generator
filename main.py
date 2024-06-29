import logging
import os

from utils.generator_logging import setup_logging
from utils.generator_toml import load_config
from utils.generator_json import load_json
from css.css import generate_css


def save_file(content: dict, output_dir: str, file_name: str) -> None:
    """Saves the content to a file.

    Args:
        content (str): The content to save.
        output_dir (str): The directory to save the file in.
        file_name (str): The name of the file.
    """
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/{file_name}", 'w') as file:
        # Loop through the content and write it to the file
        # The top level is the :root or :root[data-theme="theme-name"]
        # Then the next level is :root[state] or :root[data-theme="theme-name"]:[state] if the state is not default
        # Then the next level is the variable name and the value
        for key, value in content.items():
            for state, variables in value.items():
                state_modifier = f":{state}" if state != "default" else ""
                file.write(f"{key}{state_modifier} {{\n")
                for variable, value in variables.items():
                    file.write(f"\t{variable}: {value};\n")
                file.write("}\n")
    logging.info(f"Saved CSS to {output_dir}/{file_name}")


def main():
    config = load_config('config.toml')

    setup_logging(config['logging']['level'])
    logging.debug("Logging is setup.")
    logging.info("Starting the generator.")

    logging.debug(config)
    
    input_dir = config['settings']['input_dir']
    
    # Loop through each input file
    for input_file in config['settings']['input_files']:
        logging.info(f"Loading {input_file}...")
        variables = load_json(f"{input_dir}/{input_file}")
        logging.debug(variables)

        # Inside each input file, there is a list of collections, so loop through the collections
        for collection in variables['collections']:
            logging.info(f"Generating CSS for {collection['name']}...")
            variables_map = generate_css(config, collection)
            # Write the CSS to a file
            output_dir = config['css']['output']['dir']
            file_name = config['css']['output']['file']
            
            logging.info(f"Saving CSS to {output_dir}/{file_name}...")
            save_file(variables_map, output_dir, file_name)


if __name__ == '__main__':
    main()
