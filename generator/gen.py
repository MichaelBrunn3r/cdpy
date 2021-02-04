import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import requests
import typer

app = typer.Typer()


def fetch_and_save_protocol(url: str, filename_template: str) -> Tuple[int, int]:
    protocol = requests.get(url).json()

    minor = protocol["version"]["minor"]
    major = protocol["version"]["major"]

    script_dir = Path(os.path.abspath(os.path.split(__file__)[0]))
    filename = filename_template.format(major, minor)
    path = Path(script_dir, filename)

    with path.open("w") as f:
        f.write(json.dumps(protocol, indent=4))

    return (major, minor)


@app.command()
def fetch_protocol():
    version = fetch_and_save_protocol(
        "https://raw.githubusercontent.com/ChromeDevTools/devtools-protocol/master/json/browser_protocol.json",
        "browser_protocol-v{}.{}.json",
    )
    fetch_and_save_protocol(
        "https://raw.githubusercontent.com/ChromeDevTools/devtools-protocol/master/json/js_protocol.json",
        "js_protocol_v{}.{}.json",
    )

    typer.echo("Fetched protocol v{}.{}".format(version[0], version[1]))


if __name__ == "__main__":
    app()
