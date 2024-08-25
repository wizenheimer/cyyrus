from pathlib import Path


def get_ascii_art():
    return """
                                        __  ,-.          ,--,
                                    ,' ,'/ /|        ,'_ /|    .--.--.
    ,---.         .--,        .--,  '  | |' |   .--. |  | :   /  /    '
    /     \\      /_ ./|      /_ ./|  |  |   ,' ,'_ /| :  . |  |  :  /`./
    /    / '   , ' , ' :   , ' , ' :  '  :  /   |  ' | |  . .  |  :  ;_
    .    ' /   /___/ \\: |  /___/ \\: |  |  | '    |  | ' |  | |   \\  \\    `.
    '   ; :__   .  \\  ' |   .  \\  ' |  ;  : |    :  | : ;  ; |    `----.   \\
    '   | '.'|   \\  ;   :    \\  ;   :  |  , ;    '  :  `--'   \\  /  /`--'  /
    |   :    :    \\  \\  ;     \\  \\  ;   ---'     :  ,      .-./ '--'.     /
    \\   \\  /      :  \\  \\     :  \\  \\            `--`----'       `--'---'
    `----'        \\  ' ;      \\  ' ;
                    `--`        `--`
    """


def create_export_filepath(
    base_path: Path,
    dataset_name: str,
    export_format: str,
) -> Path:
    # Ensure the base path is a directory
    if base_path.is_file():
        base_path = base_path.parent

    # Create a valid filename
    valid_name = "".join(c for c in dataset_name if c.isalnum() or c in ("-", "_")).rstrip()
    filename = f"{valid_name}.{export_format}"

    return base_path / filename
