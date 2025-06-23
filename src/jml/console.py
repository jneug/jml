from rich.console import Console
from rich.theme import Theme

console_theme = Theme(
    {
        "jml.path": "cyan",
        "jml.file": "purple bold",
        "jml.name": "yellow bold",
        "jml.ver": "orange1 bold",
        "jml.err": "red bold",
        #
        "repr.number": "",
        "repr.number_complex": "",
        "repr.path": "cyan",
        "repr.filename": "cyan",
    },
)


console = Console(theme=console_theme, highlight=False)
