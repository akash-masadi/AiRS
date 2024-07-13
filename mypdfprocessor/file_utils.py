def load_file(file_path):
    try:
        with open(file_path, 'r') as file:
            rules = file.read()
        return rules
    except FileNotFoundError:
        return f"Error: The file '{file_path}' was not found."
    except IOError:
        return f"Error: An I/O error occurred while reading the file '{file_path}'."