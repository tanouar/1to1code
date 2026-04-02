"""
Configuration de l'environnement Google Colab pour les cours PySpark.
"""
from pyspark.sql import SparkSession
from sparktools.spark_monitor import SparkJobMonitor
from sparktools.spark_utils import SparkHelper


def setup_colab(app_name: str = "PySpark Course",
                memory: str = "4g",
                shuffle_partitions: int = 8):
    """
    Configure PySpark pour Google Colab :
      - Crée la SparkSession avec les options adaptées à Colab
      - Ouvre la SparkUI dans une fenêtre Colab (port 4040)
      - Initialise SparkJobMonitor et SparkHelper

    Args:
        app_name: Nom de l'application (visible dans SparkUI)
        memory:   RAM allouée au driver et aux executors (ex: "4g")
        shuffle_partitions: Nombre de partitions pour les shuffles

    Returns:
        tuple: (spark, monitor, helper)

    Exemple:
        spark, monitor, helper = setup_colab("01 - Introduction PySpark")
    """
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.driver.memory", memory) \
        .config("spark.executor.memory", memory) \
        .config("spark.sql.shuffle.partitions", str(shuffle_partitions)) \
        .getOrCreate()

    # Ouvrir la SparkUI via le tunnel Colab
    try:
        from google.colab import output
        output.serve_kernel_port_as_window(4040, path="/jobs/index.html")
        print("✓ SparkUI ouverte → cliquez sur le lien ci-dessus")
    except ImportError:
        print(f"✓ SparkUI disponible sur http://localhost:4040")

    monitor = SparkJobMonitor(spark)
    helper = SparkHelper()

    print("=" * 60)
    print(f"✓ Spark {spark.version}  |  App : {app_name}")
    print(f"✓ Memory : {memory}  |  Shuffle partitions : {shuffle_partitions}")
    print(f"✓ SparkJobMonitor et SparkHelper initialisés")
    print("=" * 60)

    return spark, monitor, helper
