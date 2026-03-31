import typer
from pathlib import Path
from typing import Optional  #first change
import requests
import os
import json
import math
import jwt as pyjwt  # pip install PyJWT

app = typer.Typer(help="Hammer: The Distributed Campus Grid")
TOKEN_FILE = Path.home() / ".hammer_token" 



def divideintochunks(file_path: Path):
    file_size_bytes = os.path.getsize(file_path)
    file_size_mb = file_size_bytes / (1024 * 1024)
    
    target_chunk_mb = 64.0 
    
    # Calculate required chunks and round up (minimum 1 chunk)
    calculated_chunks = max(1, math.ceil(file_size_mb / target_chunk_mb))
    return calculated_chunks




def get_token():
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, 'r') as f:
            token = json.load(f)["access_token"]
        try:
            # ✅ decode without verifying signature, just check expiry
            pyjwt.decode(token, options={"verify_signature": False, "verify_exp": True})
            return token                        # ✅ token still valid
        except pyjwt.ExpiredSignatureError:
            TOKEN_FILE.unlink()                 # ✅ delete expired token file
            typer.secho("Session expired, please login again!", fg=typer.colors.YELLOW)
            return None
    return None



def save_token(token: str):
    with open(TOKEN_FILE, 'w') as f:
        json.dump({"access_token": token}, f)

@app.command()
def submit(
    script: Path = typer.Argument(..., help="The Python script to execute"),
    dataset: Path = typer.Argument(..., help="The massive CSV dataset"),
    chunks: int = typer.Option(None, "--chunks", "-c", help="Number of pieces to split the data into")
):
    
    token = get_token()

    
    if not token:                                  
        typer.secho("Please login first!", fg=typer.colors.RED)
        raise typer.Exit(code=1)
        
    """
    Submit a machine learning job to the Hammer grid.
    """

        

    typer.secho(f"Initializing Hammer Protocol...", fg=typer.colors.CYAN, bold=True)
    
    
    if not script.exists():
        typer.secho(f"Error: Script '{script}' not found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    if chunks is None:
        typer.secho("🧠 No chunk count provided. Calculating optimal size...", fg=typer.colors.CYAN)
        chunks = divideintochunks(dataset)
    else:
        chunks = chunks
    
    
    typer.echo(f"Packaging {script}...")
    # typer.echo(f"Preparing to chunk {dataset} into {chunks} pieces...")

    submit_path = "http://127.0.0.1:5000/submit"

    files = {
        'dataset': open(dataset, 'rb'),
        'pyfile': open(script, 'rb')

    }

    requests.post(submit_path, files=files)
        
    typer.secho("Job successfully fired to the Central Broker!", fg=typer.colors.GREEN)
    
    print(chunks)


@app.command()
def status(job_id: str):
    """
    Check the status of a submitted job.
    """
    typer.echo(f"Pinging Central Broker for status of job: {job_id}...")


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



    response=requests.post(register_path, data=form_data)

    # print("Status code:", response.status_code)
    # print("Response body:", response.text)

    if response.status_code == 201:
        api_key = response.json()["api_key"]
        typer.secho(f"Registered! Your API key: {api_key}", fg=typer.colors.GREEN)
        typer.secho("Save this key — you'll need it for all commands!", fg=typer.colors.YELLOW)
        typer.secho(
        "\nLogin Options:\n"
        " 1. Login with Credentials (login function)\n"
        " 2. Login with API KEY (login_key function)",
        fg=typer.colors.CYAN,
        bold=True
    )


@app.command()
def loginkey(
    key: str = typer.Option(..., help="the key provided when you register")
):
    login_path="http://127.0.0.1:5000/loginkey"
    
    form_data = {
        'api_key':key
    }

    response=requests.post(login_path, data=form_data)
    name=response.text.split("and")[0]
    token=response.text.split("and")[1]

    save_token(token=token)
    if response.status_code==200:
        typer.secho(name)
    else:
        typer.secho(response.text)



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

    response=requests.post(login_path, data=form_data)
    name=response.text.split("and")[0]
    token=response.text.split("and")[1]
    save_token(token=token)
    if response.status_code == 200:
        typer.secho(name, fg=typer.colors.GREEN)
    elif response.status_code == 404:
        typer.secho("Wrong Password", fg=typer.colors.RED)
    else:
        typer.secho("User not exist", fg=typer.colors.RED)




def main():
    app()

if __name__ == "__main__":
    main()