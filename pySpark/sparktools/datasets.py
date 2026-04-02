"""
Téléchargement des datasets utilisés dans les notebooks PySpark.
"""
import os
import urllib.request


def download_iris(dest: str = "/content/iris.csv") -> str:
    """
    Télécharge le dataset Iris (UCI ML Repository).

    150 lignes | 5 colonnes | ~4 KB
    Colonnes : sepal_length, sepal_width, petal_length, petal_width, class

    Returns:
        str: chemin local du fichier CSV
    """
    if not os.path.exists(dest):
        os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
        url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
        print(f"⏳ Téléchargement Iris...")
        urllib.request.urlretrieve(url, dest)
        print(f"✓ Iris téléchargé → {dest}")
    else:
        print(f"✓ Iris déjà présent → {dest}")
    return dest


def download_ban(dest: str = "/content/adresse_france.parquet") -> str:
    """
    Télécharge le fichier Parquet de la Base Adresses Nationales (data.gouv.fr).

    ~24 millions de lignes | ~500 MB compressé en Parquet

    Returns:
        str: chemin local du fichier Parquet
    """
    if not os.path.exists(dest):
        url = "https://www.data.gouv.fr/api/1/datasets/r/3a80f74e-df4f-4d79-8735-4226e48526db"
        print("⏳ Téléchargement BAN (~500 MB) — quelques minutes...")
        urllib.request.urlretrieve(url, dest)
        size_mb = os.path.getsize(dest) / (1024 ** 2)
        print(f"✓ BAN téléchargée → {dest} ({size_mb:.0f} MB)")
    else:
        size_mb = os.path.getsize(dest) / (1024 ** 2)
        print(f"✓ BAN déjà présente → {dest} ({size_mb:.0f} MB)")
    return dest


def download_oxford_pets(dest: str = "/content/oxford_pets") -> str:
    """
    Télécharge et extrait le Oxford-IIIT Pet Dataset.

    ~7 349 images JPEG | 37 races (chats + chiens) | ~800 MB compressé

    Returns:
        str: chemin local du dossier images/ (contenant les .jpg)
    """
    images_dir = os.path.join(dest, "images")

    if not os.path.exists(images_dir):
        import requests
        import tarfile

        os.makedirs(dest, exist_ok=True)
        url = "https://www.robots.ox.ac.uk/~vgg/data/pets/data/images.tar.gz"
        tar_path = os.path.join(dest, "images.tar.gz")

        print("⏳ Téléchargement Oxford Pets (~800 MB) — 5 à 10 minutes...")
        response = requests.get(url, stream=True)
        total = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(tar_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total and downloaded % (100 * 1024 * 1024) == 0:
                        pct = downloaded / total * 100
                        print(f"  {downloaded / (1024**2):.0f} / {total / (1024**2):.0f} MB  ({pct:.0f}%)")

        print("⏳ Extraction de l'archive...")
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(dest)
        os.remove(tar_path)

    nb = len([f for f in os.listdir(images_dir) if f.endswith(".jpg")])
    print(f"✓ Oxford Pets prêt → {images_dir}  ({nb:,} images)")
    return images_dir
