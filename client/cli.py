import typer
from pathlib import Path
import requests
import os
import json
import math
from pathlib import Path

app = typer.Typer(help="Hammer: The Distributed Campus Grid")
TOKEN_FILE = Path.home() / ".hammer_token" 

@app.command()
def submit(
    script: Path = typer.Argument(..., help="The Python script to execute"),
    dataset: Path = typer.Argument(..., help="The massive CSV dataset"),
    chunks: int = typer.Option(4, "--chunks", "-c", help="Number of pieces to split the data into")
):
    """
    Submit a machine learning job to the Hammer grid.
    """
    typer.secho("Initializing Hammer Protocol...", fg=typer.colors.CYAN, bold=True)
    
    if not script.exists() or not dataset.exists():
        typer.secho("Error: Could not find the script or dataset file.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
        
    typer.echo(f"Packaging {script.name} and {dataset.name}...")
    
    url = "http://127.0.0.1:5000/submit"

    if not TOKEN_FILE.exists():
        typer.secho("Error: You must login first using 'hammer login'", fg=typer.colors.RED)
        raise typer.Exit(code=1)
        
    with open(TOKEN_FILE, "r") as f:
        token = f.read().strip()
        
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    files = {
        'pyfile': open(script, 'rb'),
        'dataset': open(dataset, 'rb')
    }

    try:
        typer.echo("Transmitting to Central Broker...")
        response = requests.post(url, data={'chunks':chunks}, files=files, headers=headers)
        
        if response.status_code == 200:
            typer.secho("Success! Job accepted by the Hammer Broker.", fg=typer.colors.GREEN)
            typer.echo(f"Server Response: {response.json().get('message', '')}")
        else:
            resp_data = response.json()
            error_text = resp_data.get('message') or resp_data.get('msg') or "Unknown Server Crash"
            typer.secho(f"Server Error: {error_text}", fg=typer.colors.RED)

    except requests.exceptions.ConnectionError:
        typer.secho("Error: Could not connect to the Central Broker. Is the server running?", fg=typer.colors.RED)

@app.command()
def register(
    email: str = typer.Option(..., prompt="email"),
    password: str = typer.Option(..., prompt=True, hide_input=True)
):
    
    register_path = "http://127.0.0.1:5000/register"

    form_data = {
        'email': email,
        'password': password
    }
    response=requests.post(register_path, json=form_data)

    if response.status_code == 201:
        typer.secho(
            "Login with you email and password",
            fg=typer.colors.CYAN,
            bold=True
        )
    else:
        typer.secho("Unable to register the user", fg=typer.colors.RED, bold=True)


@app.command()
def login(
    email: str = typer.Option(..., prompt="email"),
    password: str = typer.Option(..., prompt=True, hide_input=True)
):
    login_path = "http://127.0.0.1:5000/login"

    form_data = {
        'email': email,
        'password': password
    }
    response=requests.post(login_path, json=form_data)

    if response.status_code == 200:
        token = response.json().get("access_token")
        with open(TOKEN_FILE, "w") as f:
            f.write(token)
        typer.secho(response.json().get("message",""), fg=typer.colors.GREEN)
    elif response.status_code == 404:
        typer.secho("Wrong Password", fg=typer.colors.RED)
    else:
        typer.secho("User not exist", fg=typer.colors.RED)



def main():
    app()

if __name__ == "__main__":
    main()