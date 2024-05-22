import logging
import os

from utils.generator_logging import setup_logging
from utils.generator_toml import load_config
from utils.generator_json import load_json
from css.css import generate_css


def save_file(content: str, output_dir: str, file_name: str) -> None:
    """Saves the content to a file.

    Args:
        content (str): The content to save.
        output_dir (str): The directory to save the file in.
        file_name (str): The name of the file.
    """
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/{file_name}", 'w') as file:
        file.write(content)


def main():
    config = load_config('config.toml')

    setup_logging(config['logging']['level'])
    logging.debug("Logging is setup.")
    logging.info("Starting the generator.")

    logging.debug(config)

    # Go through each input file and get the variables/process them
    for input_file in config['settings']['input_files']:
        full_input_file = config['settings']['input_dir'] + '/' + input_file
        logging.info(f"Processing {full_input_file}")
        variables = load_json(full_input_file)
        css_content = generate_css(variables, config)
        save_file(css_content, config['css']['output']
                  ['dir'], f"{os.path.splitext(input_file)[0]}.css")
        logging.info(f"Finished processing {input_file}")


if __name__ == '__main__':
    main()
