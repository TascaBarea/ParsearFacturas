
import typer
from pathlib import Path
from .patterns import load_patterns

app = typer.Typer(help='FACTURAS CLI')

@app.command()
def check_patterns(dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True)):
    patterns = load_patterns(dir)
    typer.echo(f'Patrones cargados: {len(patterns)}')

if __name__ == '__main__':
    app()
