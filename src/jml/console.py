from rich.console import Console
from rich.theme import Theme

console_theme = Theme(
    {"path": "cyan", "file": "purple", "name": "yellow bold", "ver": "orange1 bold"}
)


console = Console(theme=console_theme)
