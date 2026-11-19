"""
Bibliothèque d'utilitaires Spark
"""

from .spark_monitor import SparkJobMonitor, track_spark_job, execute_with_job_tracking
from .spark_utils import SparkHelper
from .colab_setup import setup_colab
from .datasets import download_iris, download_ban, download_oxford_pets
from .image_utils import (
    extract_image_info,
    build_metadata_pipeline,
    add_image_dimensions,
    resize_images,
)
from .image_display import show_image_grid, show_before_after

__all__ = [
    # Monitoring
    'SparkJobMonitor',
    'track_spark_job',
    'execute_with_job_tracking',
    # Helpers
    'SparkHelper',
    # Colab
    'setup_colab',
    # Datasets
    'download_iris',
    'download_ban',
    'download_oxford_pets',
    # Images — traitement
    'extract_image_info',
    'build_metadata_pipeline',
    'add_image_dimensions',
    'resize_images',
    # Images — affichage
    'show_image_grid',
    'show_before_after',
]

__version__ = '1.2.0'