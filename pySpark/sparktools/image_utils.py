"""
Utilitaires pour le traitement distribué d'images avec PySpark.

Fournit :
  - extract_image_info : UDF qui extrait width/height/channels/format
  - build_metadata_pipeline : transformations lazy sur les noms de fichiers
  - add_image_dimensions : applique l'UDF et aplatit les colonnes résultantes
"""
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, IntegerType, StringType
from pyspark.sql.functions import udf


# ── Schéma de retour de l'UDF ────────────────────────────────────────────────

_IMAGE_INFO_SCHEMA = StructType([
    StructField("width",    IntegerType(), True),
    StructField("height",   IntegerType(), True),
    StructField("channels", IntegerType(), True),
    StructField("format",   StringType(),  True),
])


# ── UDF de décodage ──────────────────────────────────────────────────────────

@udf(returnType=_IMAGE_INFO_SCHEMA)
def extract_image_info(image_bytes):
    """
    UDF Spark : extrait les métadonnées d'une image depuis ses octets bruts.

    Exécutée en parallèle sur chaque worker pour chaque ligne du DataFrame.
    Utilise Pillow pour décoder l'image sans l'écrire sur disque.

    Args:
        image_bytes: colonne 'content' (binary) issue de spark.read.format("binaryFile")

    Returns:
        Struct { width, height, channels, format } ou None si l'image est corrompue
    """
    try:
        from PIL import Image
        import io

        img = Image.open(io.BytesIO(image_bytes))
        channels_map = {"RGB": 3, "RGBA": 4, "L": 1}
        channels = channels_map.get(img.mode, len(img.getbands()))

        return {
            "width":    img.width,
            "height":   img.height,
            "channels": channels,
            "format":   img.format,
        }
    except Exception:
        return None


# ── Pipelines de transformation ──────────────────────────────────────────────

def build_metadata_pipeline(df_images: DataFrame) -> DataFrame:
    """
    Pipeline de transformations LAZY pour extraire les métadonnées
    depuis les noms de fichiers du dataset Oxford-IIIT Pets.

    Format attendu : 'Abyssinian_1.jpg', 'golden_retriever_42.jpg'
    Convention du dataset : races de chats → PremièreLettreMajuscule

    Colonnes ajoutées :
      - filename  : nom du fichier (sans le chemin)
      - race_raw  : nom brut de la race (avec underscores)
      - race      : nom normalisé de la race (espaces)
      - image_id  : identifiant entier de l'image
      - species   : "Cat" ou "Dog"
      - size_mb   : taille du fichier en MB

    Args:
        df_images: DataFrame issu de spark.read.format("binaryFile")

    Returns:
        DataFrame enrichi (aucune action déclenchée — lazy)
    """
    return (
        df_images
        .withColumn("filename",
            F.element_at(F.split(F.col("path"), "/"), -1))
        .withColumn("race_raw",
            F.regexp_replace(F.col("filename"), r"_\d+\.jpg$", ""))
        .withColumn("race",
            F.regexp_replace(F.col("race_raw"), "_", " "))
        .withColumn("image_id",
            F.regexp_extract(F.col("filename"), r"_(\d+)\.jpg$", 1).cast("int"))
        .withColumn("species",
            F.when(F.col("race_raw").rlike(r"^[A-Z][a-z]+"), "Cat")
             .otherwise("Dog"))
        .withColumn("size_mb",
            (F.col("length") / (1024 * 1024)).cast("decimal(10,2)"))
    )


def add_image_dimensions(df_with_meta: DataFrame) -> DataFrame:
    """
    Applique l'UDF extract_image_info de façon LAZY et aplatit
    les champs du struct résultant en colonnes top-level.

    Colonnes ajoutées :
      - width, height   : dimensions en pixels
      - channels        : nombre de canaux (1=gris, 3=RGB, 4=RGBA)
      - format          : format détecté par Pillow (ex: "JPEG")
      - pixels          : width × height
      - aspect_ratio    : largeur / hauteur (2 décimales)

    ⚠️  L'action déclenchante (show, count…) sera lente :
        chaque image est décompressée par Pillow sur les workers.

    Args:
        df_with_meta: DataFrame enrichi par build_metadata_pipeline()

    Returns:
        DataFrame avec les colonnes de dimensions (lazy)
    """
    return (
        df_with_meta
        .withColumn("_info", extract_image_info(F.col("content")))
        .withColumn("width",        F.col("_info.width"))
        .withColumn("height",       F.col("_info.height"))
        .withColumn("channels",     F.col("_info.channels"))
        .withColumn("format",       F.col("_info.format"))
        .withColumn("pixels",       F.col("width") * F.col("height"))
        .withColumn("aspect_ratio", (F.col("width") / F.col("height")).cast("decimal(10,2)"))
        .drop("_info")
    )
