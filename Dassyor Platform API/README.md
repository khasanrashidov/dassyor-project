# Dassyor 🚀

### Important commands

#### Virtual environment

To create a virtual environment, use the following command, within the project directory, enter the following commands:

- Windows:

```powershell
py -3 -m venv .venv
```

```powershell
.venv\Scripts\activate
```

- MacOS/Linux:

```bash
python3 -m venv .venv
```

```bash
. .venv/bin/activate
```

#### Installation of dependencies

To install the required dependencies for the project, you can use the following command:

```bash
pip install -r requirements.txt
```

#### Generating requirements.txt

To generate a `requirements.txt` file with the current environment's packages, use the following command:

```bash
pip freeze > requirements.txt
```

#### Running the project (Flask)

To run the project locally, use the following command in src directory:

```bash
python -m flask run
```

To run the project in external host, use the following command in src directory:

```bash
python -m flask run --host=0.0.0.0
```

#### Migration Commands Reference

- Initialize migrations (once)

```bash
flask db init
```

- Generate new migration

```bash
flask db migrate -m "migration message"
```

- Apply migrations

```bash
flask db upgrade
```

- Rollback migrations

```bash
flask db downgrade
```

- Show current migration

```bash
flask db current
```

- Show migration history

```bash
flask db history
```

#### To delete the **pycache** run:

- Windows

```powershell
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
```

- MacOS

```bash
find . -type d -name "__pycache__" -exec rm -r {} +
```

#### Import sorting with isort

- To sort imports, use the following command:

```bash
isort .
```

#### Formatting with black

- To format the code, use the following command:

```bash
black .
```
