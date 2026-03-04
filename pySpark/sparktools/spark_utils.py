"""
Utilitaires Spark pour faciliter le développement
"""

from pyspark.sql import DataFrame
from typing import List


class SparkHelper:
    """Classe d'aide pour les opérations Spark courantes"""
    
    @staticmethod
    def show_dataframe_info(df: DataFrame, name: str = "DataFrame") -> None:
        """
        Affiche les informations complètes d'un DataFrame
        
        Args:
            df: DataFrame Spark
            name: Nom du DataFrame
        """
        print(f"\n{'='*60}")
        print(f"📊 Informations sur: {name}")
        print(f"{'='*60}")
        
        print(f"\n🔢 Nombre de lignes: {df.count():,}")
        print(f"📋 Nombre de colonnes: {len(df.columns)}")
        
        print(f"\n📝 Schéma:")
        df.printSchema()
        
        print(f"\n👀 Aperçu des données:")
        df.show(5, truncate=False)
        
        print(f"\n📈 Statistiques:")
        df.describe().show()
    
    @staticmethod
    def compare_dataframes(df1: DataFrame, df2: DataFrame, 
                          name1: str = "DF1", name2: str = "DF2") -> None:
        """
        Compare deux DataFrames
        
        Args:
            df1: Premier DataFrame
            df2: Second DataFrame
            name1: Nom du premier DataFrame
            name2: Nom du second DataFrame
        """
        print(f"\n{'='*60}")
        print(f"🔍 Comparaison: {name1} vs {name2}")
        print(f"{'='*60}")
        
        count1 = df1.count()
        count2 = df2.count()
        
        print(f"\n📊 Nombre de lignes:")
        print(f"   {name1}: {count1:,}")
        print(f"   {name2}: {count2:,}")
        print(f"   Différence: {abs(count1 - count2):,}")
        
        print(f"\n📋 Colonnes:")
        print(f"   {name1}: {df1.columns}")
        print(f"   {name2}: {df2.columns}")
        
        common_cols = set(df1.columns) & set(df2.columns)
        print(f"   Colonnes communes: {len(common_cols)}")
    
    @staticmethod
    def get_partition_info(df: DataFrame) -> None:
        """
        Affiche les informations sur le partitionnement
        
        Args:
            df: DataFrame Spark
        """
        num_partitions = df.rdd.getNumPartitions()
        
        print(f"\n{'='*60}")
        print(f"🗂️  Informations de Partitionnement")
        print(f"{'='*60}")
        print(f"\n📦 Nombre de partitions: {num_partitions}")
        
        # Obtenir la distribution des lignes par partition
        partition_sizes = df.rdd.glom().map(len).collect()
        
        print(f"\n📊 Distribution des lignes par partition:")
        print(f"   Min: {min(partition_sizes):,}")
        print(f"   Max: {max(partition_sizes):,}")
        print(f"   Moyenne: {sum(partition_sizes) / len(partition_sizes):,.0f}")
        
        if len(partition_sizes) <= 10:
            print(f"\n📋 Détail par partition:")
            for i, size in enumerate(partition_sizes):
                print(f"   Partition {i}: {size:,} lignes")