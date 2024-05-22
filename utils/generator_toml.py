import toml


def load_config(file_path):
    with open(file_path, 'r') as file:
        return toml.load(file)
