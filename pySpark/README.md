# PySpark Utils

Utilitaires PySpark pour le monitoring de jobs, le traitement d'images et la gestion de datasets.

## Installation

```bash
# Colab
!pip install -q pyspark findspark
!git clone --filter=blob:none --sparse https://github.com/tanouar/1to1code.git -q \
  && cd 1to1code && git sparse-checkout set pySpark -q

# Local
pip install git+https://github.com/tanouar/1to1code.git#subdirectory=pySpark
```

## Utilisation

```python
# Setup Colab (SparkSession + monitor + helper)
from sparktools.colab_setup import setup_colab
spark, monitor, helper = setup_colab("Mon projet")

# Monitoring
monitor.execute_and_monitor(lambda: df.count(), "Comptage")
monitor.show_history()

# Helpers DataFrame
helper.show_dataframe_info(df, "Mon DataFrame")
helper.get_partition_info(df)

# Datasets
from sparktools.datasets import download_iris, download_ban, download_oxford_pets
```

## Structure

```
sparktools/
├── colab_setup.py   # SparkSession + setup Colab
├── spark_monitor.py # Monitoring des jobs
├── spark_utils.py   # Helpers DataFrame
├── datasets.py      # Téléchargement de datasets
└── image_utils.py   # Utilitaires images
notebooks/           # 4 notebooks pédagogiques
```

## Notebooks

| # | Thème |
|---|-------|
| 01 | Introduction PySpark & SparkUI |
| 02 | Traitement CSV |
| 03 | Traitement Parquet |
| 04 | Traitement d'images |
