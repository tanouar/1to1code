# PySpark Utils

Bibliothèque d'utilitaires pour Apache Spark / PySpark développée pour faciliter le traitement distribué de données et d'images.

## 🎯 Fonctionnalités

- **Monitoring** : Suivi des jobs Spark avec historique et visualisations
- **Traitement d'images** : Chargement, transformation et extraction de features
- **Gestion de données** : Optimisation Parquet, partitionnement intelligent
- **Helpers** : Utilitaires pour DataFrames, performance, validation
- **Configuration** : SparkSession builder avec configs prédéfinies

## 📦 Installation

### Via GitHub
```bash
pip install git+https://github.com/tanouar/1to1code.git#subdirectory=pySpark
```

### Via clone local
```bash
git clone https://github.com/tanouar/1to1code.git
cd 1to1code/pySpark
pip install -e .
```

### Dans Google Colab
```python
!git clone https://github.com/tanouar/1to1code.git
!pip install ./1to1code/pySpark --break-system-packages -q
```

## 🚀 Utilisation Rapide

### Monitoring des Jobs
```python
from pyspark_utils.monitoring import SparkJobMonitor

monitor = SparkJobMonitor(spark)
result = monitor.execute_and_monitor(
    lambda: df.count(), 
    "Mon premier job"
)
monitor.show_history()
monitor.show_chart()
```

### Traitement d'Images
```python
from pyspark_utils.images import ImageLoader, ImageTransformer

# Chargement
loader = ImageLoader(spark)
df_images = loader.load_images("/path/to/images", with_metadata=True)

# Transformation
transformer = ImageTransformer()
df_resized = transformer.resize(df_images, width=224, height=224)
df_features = transformer.extract_color_features(df_resized)
```

### Gestion de Données
```python
from pyspark_utils.data import ParquetLoader, PartitioningHelper

# Chargement optimisé
loader = ParquetLoader(spark)
df = loader.load("/path/to/data.parquet")

# Suggestions de partitionnement
helper = PartitioningHelper()
suggestions = helper.suggest_partitions(df, ["date", "region"])
```

### Helpers DataFrame
```python
from pyspark_utils.helpers import DataFrameHelper

helper = DataFrameHelper()
helper.show_info(df, name="Mon DataFrame")
helper.get_partition_info(df)
```

## 📚 Documentation

Voir le dossier [docs/](docs/) pour la documentation complète :

- [Guide de Monitoring](docs/monitoring.md)
- [Guide Traitement d'Images](docs/images.md)
- [Guide Gestion de Données](docs/data.md)
- [Référence API](docs/api_reference.md)

## 📁 Structure du Projet

```
pyspark-utils/
├── pyspark_utils/          # Package principal
│   ├── monitoring/         # Monitoring Spark
│   ├── images/            # Traitement d'images
│   ├── data/              # Gestion de données
│   ├── helpers/           # Helpers génériques
│   ├── config/            # Configuration Spark
│   └── utils/             # Utilitaires
├── examples/              # Exemples d'utilisation
├── docs/                  # Documentation
└── tests/                 # Tests unitaires (à venir)
```

## 🎓 Exemples

Consultez le dossier [examples/](examples/) pour des exemples complets :

- `example_monitoring.py` : Monitoring de jobs
- `example_images.py` : Traitement d'images
- `example_partitioning.py` : Partitionnement de données
- `notebook_1_parquet.ipynb` : Notebook complet sur Parquet
- `notebook_2_images.ipynb` : Notebook complet sur les images

## 🤝 Contribution

Les contributions sont bienvenues ! N'hésitez pas à ouvrir des issues ou des pull requests.

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE)

## ✨ Auteur

Développé dans le cadre d'un projet d'apprentissage PySpark
