import sys
from pathlib import Path

# Ajoute le dossier server/ au path pour pouvoir importer csv_repository, models, etc.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "server"))
