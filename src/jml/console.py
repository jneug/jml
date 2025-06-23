from rich.console import Console
from rich.theme import Theme

console_theme = Theme(
    {
        "path": "cyan",
        "file": "purple",
        "name": "yellow bold",
        "ver": "orange1 bold",
        "err": "red bold",
        #
        "repr.number": "",
        "repr.number_complex": "",
        "repr.path": "cyan",
        "repr.filename": "cyan",
    },
)


console = Console(theme=console_theme)
