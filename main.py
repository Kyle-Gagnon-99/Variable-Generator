import toml


def load_config(config_path):
    with open(config_path, 'r') as f:
        return toml.load(f)


def main():
    config = load_config('config.toml')
    print(config)


if __name__ == '__main__':
    main()
