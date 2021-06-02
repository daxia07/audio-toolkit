from pathlib import Path

from dotenv import dotenv_values

CWD = Path(__file__).absolute().parent
config = dotenv_values(".env")
