"""
Fonctions d'affichage d'images pour les notebooks PySpark.

Les images sont collectées sur le driver (petit échantillon via .take(n))
puis affichées avec matplotlib — sans impacter les workers Spark.

Fournit :
  - show_image_grid    : grille d'images avec label race + espèce
  - show_before_after  : comparaison avant/après redimensionnement
"""
import io
import math

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from PIL import Image


def show_image_grid(df, n=12, title="Aperçu du dataset"):
    """
    Affiche une grille de n images avec leur race et espèce.

    Collecte les n premières lignes sur le driver (petite quantité),
    puis décode et affiche côte à côte avec matplotlib.

    Args:
        df    : DataFrame Spark avec colonnes 'content', 'race', 'species'
        n     : nombre d'images à afficher (défaut : 12)
        title : titre affiché au-dessus de la grille
    """
    rows = df.select("content", "race", "species").limit(n).collect()

    cols = 4
    lines = math.ceil(len(rows) / cols)
    fig, axes = plt.subplots(lines, cols, figsize=(cols * 3.5, lines * 3.2))
    axes = axes.flatten() if lines > 1 else [axes] if cols == 1 else axes.flatten()

    for i, row in enumerate(rows):
        img = Image.open(io.BytesIO(bytes(row["content"]))).convert("RGB")
        axes[i].imshow(img)
        color = "#4C81AD" if row["species"] == "Cat" else "#4CADA8"
        axes[i].set_title(
            f"{row['race']}\n({row['species']})",
            fontsize=9, color=color, fontweight="bold"
        )
        axes[i].axis("off")

    # Masquer les axes vides si n n'est pas un multiple de cols
    for j in range(len(rows), len(axes)):
        axes[j].axis("off")

    # Légende espèces
    legend = [
        mpatches.Patch(color="#4C81AD", label="Chat"),
        mpatches.Patch(color="#4CADA8", label="Chien"),
    ]
    fig.legend(handles=legend, loc="lower center", ncol=2,
               fontsize=10, frameon=False, bbox_to_anchor=(0.5, -0.02))

    fig.suptitle(title, fontsize=13, fontweight="bold", y=1.01)
    plt.tight_layout()
    plt.show()


def show_before_after(df_original, df_resized, n=4):
    """
    Affiche n images en deux lignes : originales (haut) et redimensionnées (bas).

    Permet de visualiser l'effet du redimensionnement distribué.
    Les dimensions originales et cibles sont affichées sous chaque image.

    Args:
        df_original : DataFrame avec colonnes 'content', 'race', 'width', 'height'
        df_resized  : DataFrame avec colonnes 'resized_content',
                      'resized_width', 'resized_height' (même ordre de lignes)
        n           : nombre de paires à afficher (défaut : 4)
    """
    orig_rows = df_original.select(
        "content", "race", "width", "height"
    ).limit(n).collect()

    resized_rows = df_resized.select(
        "resized_content", "resized_width", "resized_height"
    ).limit(n).collect()

    fig, axes = plt.subplots(2, n, figsize=(n * 3.5, 7))

    for i in range(len(orig_rows)):
        # Ligne du haut — image originale
        img_orig = Image.open(io.BytesIO(bytes(orig_rows[i]["content"]))).convert("RGB")
        axes[0][i].imshow(img_orig)
        axes[0][i].set_title(
            f"{orig_rows[i]['race']}\n"
            f"{orig_rows[i]['width']}×{orig_rows[i]['height']} px",
            fontsize=9
        )
        axes[0][i].axis("off")

        # Ligne du bas — image redimensionnée
        img_resized = Image.open(
            io.BytesIO(bytes(resized_rows[i]["resized_content"]))
        ).convert("RGB")
        axes[1][i].imshow(img_resized)
        axes[1][i].set_title(
            f"{resized_rows[i]['resized_width']}×{resized_rows[i]['resized_height']} px\n"
            f"(redimensionnée)",
            fontsize=9, color="#4CADA8"
        )
        axes[1][i].axis("off")

    # Étiquettes de ligne
    axes[0][0].set_ylabel("Originale", fontsize=11, fontweight="bold", labelpad=8)
    axes[1][0].set_ylabel("Redimensionnée", fontsize=11,
                           fontweight="bold", color="#4CADA8", labelpad=8)

    fig.suptitle("Avant / Après redimensionnement (224×224 px)",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.show()
