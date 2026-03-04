"""
Module de monitoring des jobs Spark
Permet de tracker l'exécution des jobs et d'afficher les métriques
"""

import time
import uuid
from typing import Callable, Any, List, Dict
from functools import wraps


class SparkJobMonitor:
    """
    Moniteur avancé pour les jobs Spark
    
    Usage:
        monitor = SparkJobMonitor(spark)
        monitor.execute_and_monitor(lambda: df.count(), "Mon job")
        monitor.show_history()
    """
    
    def __init__(self, spark):
        """
        Initialise le moniteur
        
        Args:
            spark: SparkSession
        """
        self.spark = spark
        self.tracker = spark.sparkContext.statusTracker()
        self.job_history = []
    
    def execute_and_monitor(self, func: Callable, name: str) -> Any:
        """
        Exécute et monitore un job Spark
        
        Args:
            func: Fonction à exécuter (doit contenir une action Spark)
            name: Nom descriptif du job
            
        Returns:
            Le résultat de la fonction exécutée
        """
        # Configuration
        job_id = str(uuid.uuid4())[:8]
        self.spark.sparkContext.setJobGroup(job_id, name)
        
        print(f"\n{'='*60}")
        print(f"🔵 {name}")
        print(f"{'='*60}")
        print(f"📌 Tracking ID: {job_id}")
        
        # Exécution
        start_time = time.time()
        
        try:
            result = func()
            elapsed = time.time() - start_time
            status = "✅ SUCCESS"
            error = None
        except Exception as e:
            elapsed = time.time() - start_time
            status = "❌ FAILED"
            error = str(e)
            result = None
            print(f"\n❌ Erreur: {error}")
        
        # Récupérer les infos des jobs Spark
        spark_job_ids = list(self.tracker.getJobIdsForGroup(job_id))
        
        # Récupérer les détails des stages
        stage_info = []
        for job_id_num in spark_job_ids:
            job_info = self.tracker.getJobInfo(job_id_num)
            if job_info:
                # stageIds est un attribut, pas une méthode
                stage_ids = job_info.stageIds
                for stage_id in stage_ids:
                    stage_details = self.tracker.getStageInfo(stage_id)
                    if stage_details:
                        stage_info.append({
                            'stage_id': stage_id,
                            'num_tasks': stage_details.numTasks
                        })
        
        # Enregistrer dans l'historique
        job_record = {
            'name': name,
            'tracking_id': job_id,
            'spark_job_ids': spark_job_ids,
            'stages': stage_info,
            'duration': elapsed,
            'status': status,
            'error': error,
            'timestamp': time.time()
        }
        self.job_history.append(job_record)
        
        # Affichage
        print(f"\n{status}")
        print(f"⏱️  Durée: {elapsed:.2f}s")
        print(f"📊 Spark Job ID(s): {spark_job_ids}")
        
        if stage_info:
            total_tasks = sum(s['num_tasks'] for s in stage_info)
            print(f"📦 Stages: {len(stage_info)} | Tasks: {total_tasks}")
        
        print(f"🌐 Spark UI: http://localhost:4040/jobs/")
        
        # Réinitialiser le job group (CORRECTION ICI)
        self.spark.sparkContext.setLocalProperty("spark.jobGroup.id", None)
        
        return result
    
    def show_history(self) -> None:
        """Affiche l'historique complet des jobs exécutés"""
        print("\n" + "="*60)
        print("📜 HISTORIQUE DES JOBS")
        print("="*60)
        
        if not self.job_history:
            print("\n⚠️  Aucun job enregistré")
            return
        
        total_duration = sum(job['duration'] for job in self.job_history)
        success_count = sum(1 for job in self.job_history if job['status'] == "✅ SUCCESS")
        
        print(f"\n📊 Statistiques globales:")
        print(f"   Total jobs: {len(self.job_history)}")
        print(f"   Réussis: {success_count}")
        print(f"   Échoués: {len(self.job_history) - success_count}")
        print(f"   Durée totale: {total_duration:.2f}s")
        print(f"\n{'='*60}")
        
        for i, job in enumerate(self.job_history, 1):
            print(f"\n{i}. {job['name']}")
            print(f"   Tracking ID: {job['tracking_id']}")
            print(f"   Spark Job IDs: {job['spark_job_ids']}")
            
            if job['stages']:
                total_tasks = sum(s['num_tasks'] for s in job['stages'])
                print(f"   Stages: {len(job['stages'])} | Tasks: {total_tasks}")
            
            print(f"   Durée: {job['duration']:.2f}s")
            print(f"   Status: {job['status']}")
            
            if job['error']:
                print(f"   Erreur: {job['error']}")
    
    def get_last_job(self) -> Dict:
        """Retourne les informations du dernier job exécuté"""
        if self.job_history:
            return self.job_history[-1]
        return None
    
    def clear_history(self) -> None:
        """Efface l'historique des jobs"""
        self.job_history = []
        print("✓ Historique effacé")
    
    def get_job_stats(self) -> Dict:
        """Retourne les statistiques globales"""
        if not self.job_history:
            return {
                'total_jobs': 0,
                'success': 0,
                'failed': 0,
                'total_duration': 0,
                'avg_duration': 0
            }
        
        total_duration = sum(job['duration'] for job in self.job_history)
        success_count = sum(1 for job in self.job_history if job['status'] == "✅ SUCCESS")
        
        return {
            'total_jobs': len(self.job_history),
            'success': success_count,
            'failed': len(self.job_history) - success_count,
            'total_duration': total_duration,
            'avg_duration': total_duration / len(self.job_history)
        }


def track_spark_job(description: str):
    """
    Décorateur pour tracker un job Spark
    
    Usage:
        @track_spark_job("Mon calcul important")
        def my_function():
            return df.count()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Récupérer la SparkSession depuis les arguments ou le contexte global
            spark = kwargs.get('spark')
            if not spark:
                # Essayer de récupérer depuis les globals
                import sys
                spark = sys.modules['__main__'].__dict__.get('spark')
            
            if spark:
                spark.sparkContext.setJobDescription(description)
            
            print(f"\n🔵 {description}")
            print("=" * 60)
            
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            print(f"\n✅ Terminé en {elapsed:.2f}s")
            print(f"🌐 Spark UI: http://localhost:4040/jobs/")
            
            return result
        return wrapper
    return decorator


def execute_with_job_tracking(spark, action_func: Callable, description: str) -> Any:
    """
    Fonction utilitaire pour exécuter une action avec tracking
    
    Args:
        spark: SparkSession
        action_func: Fonction contenant l'action Spark
        description: Description du job
        
    Returns:
        Résultat de l'action
    """
    spark.sparkContext.setJobDescription(description)
    
    print(f"\n🔵 {description}")
    print("=" * 60)
    print("⏳ Exécution en cours...")
    
    start_time = time.time()
    result = action_func()
    elapsed = time.time() - start_time
    
    print(f"\n✅ Terminé en {elapsed:.2f}s")
    print(f"🌐 Spark UI: http://localhost:4040/jobs/")
    
    return result