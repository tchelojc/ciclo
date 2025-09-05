# No __init__.py da pasta data/, adicione:
import os
print("Arquivos em data/:", os.listdir(os.path.dirname(__file__)))