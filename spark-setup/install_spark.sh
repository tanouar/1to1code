#!/bin/bash

#############################################
# Script d'installation Apache Spark
# Ubuntu Server 22.04 LTS
# Avec PySpark, Jupyter et dépendances
#############################################

set -e  # Arrêt en cas d'erreur

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction de logging
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Variables de configuration
SPARK_VERSION="3.5.0"
HADOOP_VERSION="3"
SPARK_PACKAGE="spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}"
SPARK_DOWNLOAD_URL="https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/${SPARK_PACKAGE}.tgz"
INSTALL_DIR="/opt/spark"
JAVA_VERSION="11"

log_info "=== Début de l'installation Apache Spark ==="
log_info "Version Spark: ${SPARK_VERSION}"
log_info "Répertoire d'installation: ${INSTALL_DIR}"

#############################################
# Phase 1: Préparation Système
#############################################
log_info "Phase 1/7: Mise à jour du système"

sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install -y wget curl vim git software-properties-common

log_info "Phase 1/7: Terminée ✓"

#############################################
# Phase 2: Installation Java
#############################################
log_info "Phase 2/7: Installation Java ${JAVA_VERSION}"

sudo apt-get install -y openjdk-${JAVA_VERSION}-jdk

# Vérification Java
JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))
export JAVA_HOME
log_info "JAVA_HOME: ${JAVA_HOME}"
java -version

log_info "Phase 2/7: Terminée ✓"

#############################################
# Phase 3: Installation Python et dépendances
#############################################
log_info "Phase 3/7: Installation Python et pip"

sudo apt-get install -y python3 python3-pip python3-venv
python3 --version
pip3 --version

log_info "Phase 3/7: Terminée ✓"

#############################################
# Phase 4: Téléchargement et installation Spark
#############################################
log_info "Phase 4/7: Téléchargement Apache Spark"

cd /tmp
if [ -f "${SPARK_PACKAGE}.tgz" ]; then
    log_warn "Archive Spark déjà présente, suppression..."
    rm -f "${SPARK_PACKAGE}.tgz"
fi

log_info "Téléchargement depuis ${SPARK_DOWNLOAD_URL}"
wget -q --show-progress "${SPARK_DOWNLOAD_URL}"

log_info "Extraction de l'archive..."
tar -xzf "${SPARK_PACKAGE}.tgz"

log_info "Installation dans ${INSTALL_DIR}"
sudo mkdir -p ${INSTALL_DIR}
sudo mv "${SPARK_PACKAGE}"/* ${INSTALL_DIR}/
sudo chown -R $USER:$USER ${INSTALL_DIR}

# Nettoyage
rm -f "${SPARK_PACKAGE}.tgz"
rm -rf "${SPARK_PACKAGE}"

log_info "Phase 4/7: Terminée ✓"

#############################################
# Phase 5: Configuration des variables d'environnement
#############################################
log_info "Phase 5/7: Configuration des variables d'environnement"

# Ajout dans .bashrc si pas déjà présent
if ! grep -q "SPARK_HOME" ~/.bashrc; then
    cat >> ~/.bashrc << EOF

# Apache Spark Configuration
export SPARK_HOME=${INSTALL_DIR}
export PATH=\$PATH:\$SPARK_HOME/bin:\$SPARK_HOME/sbin
export PYSPARK_PYTHON=python3
export JAVA_HOME=${JAVA_HOME}
EOF
    log_info "Variables ajoutées à ~/.bashrc"
else
    log_warn "Variables Spark déjà présentes dans ~/.bashrc"
fi

# Application immédiate des variables
export SPARK_HOME=${INSTALL_DIR}
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
export PYSPARK_PYTHON=python3

log_info "Phase 5/7: Terminée ✓"

#############################################
# Phase 6: Configuration Spark
#############################################
log_info "Phase 6/7: Configuration Spark"

# Configuration spark-env.sh
cat > ${SPARK_HOME}/conf/spark-env.sh << 'EOF'
#!/usr/bin/env bash

# Configuration pour VM avec 4 cores et 16-32GB RAM
export SPARK_MASTER_HOST=localhost
export SPARK_WORKER_CORES=3
export SPARK_WORKER_MEMORY=8g
export SPARK_DRIVER_MEMORY=8g
EOF

chmod +x ${SPARK_HOME}/conf/spark-env.sh
log_info "spark-env.sh configuré"

# Configuration spark-defaults.conf
cat > ${SPARK_HOME}/conf/spark-defaults.conf << 'EOF'
# Configuration par défaut Spark
spark.master                     local[4]
spark.driver.memory              8g
spark.executor.memory            8g
spark.executor.cores             3
spark.sql.shuffle.partitions     12
spark.ui.port                    4040
spark.serializer                 org.apache.spark.serializer.KryoSerializer
spark.driver.maxResultSize       2g
spark.sql.adaptive.enabled       true
spark.sql.adaptive.coalescePartitions.enabled true
EOF

log_info "spark-defaults.conf configuré"

# Configuration log4j (réduire la verbosité)
cp ${SPARK_HOME}/conf/log4j2.properties.template ${SPARK_HOME}/conf/log4j2.properties 2>/dev/null || true

log_info "Phase 6/7: Terminée ✓"

#############################################
# Phase 7: Installation PySpark et bibliothèques Python
#############################################
log_info "Phase 7/7: Installation PySpark et bibliothèques Python"

pip3 install --upgrade pip --break-system-packages

log_info "Installation de PySpark..."
pip3 install pyspark==${SPARK_VERSION} --break-system-packages

log_info "Installation de pandas, numpy, matplotlib..."
pip3 install pandas numpy matplotlib seaborn --break-system-packages

log_info "Installation de Jupyter Notebook..."
pip3 install jupyter notebook ipython --break-system-packages

# Configuration PySpark avec Jupyter
if ! grep -q "PYSPARK_DRIVER_PYTHON" ~/.bashrc; then
    cat >> ~/.bashrc << 'EOF'

# PySpark avec Jupyter
export PYSPARK_DRIVER_PYTHON=jupyter
export PYSPARK_DRIVER_PYTHON_OPTS='notebook --no-browser --ip=0.0.0.0 --port=8888'
EOF
    log_info "Configuration Jupyter ajoutée à ~/.bashrc"
fi

log_info "Phase 7/7: Terminée ✓"

#############################################
# Création du répertoire de travail
#############################################
log_info "Création du répertoire de travail"

WORKSPACE_DIR="$HOME/spark-workspace"
mkdir -p ${WORKSPACE_DIR}
mkdir -p ${WORKSPACE_DIR}/data
mkdir -p ${WORKSPACE_DIR}/notebooks
mkdir -p ${WORKSPACE_DIR}/scripts

# Création d'un fichier de test
cat > ${WORKSPACE_DIR}/scripts/test_spark.py << 'EOF'
#!/usr/bin/env python3
"""
Script de test Apache Spark
"""
from pyspark.sql import SparkSession

print("=== Test Apache Spark ===")

# Création de la SparkSession
spark = SparkSession.builder \
    .appName("Test Installation") \
    .getOrCreate()

print(f"Spark Version: {spark.version}")
print(f"Spark Master: {spark.sparkContext.master}")

# Test simple
data = [("Alice", 25), ("Bob", 30), ("Charlie", 35)]
df = spark.createDataFrame(data, ["nom", "age"])

print("\n=== DataFrame de test ===")
df.show()

print("\n=== Statistiques ===")
df.describe().show()

# Test de calcul
result = spark.range(1, 1000000).selectExpr("sum(id) as total").collect()
print(f"\nTest de calcul: Somme de 1 à 999999 = {result[0]['total']}")

print("\n✓ Spark fonctionne correctement !")
print(f"✓ Spark UI disponible sur: http://localhost:4040")

spark.stop()
EOF

chmod +x ${WORKSPACE_DIR}/scripts/test_spark.py

log_info "Répertoire de travail créé: ${WORKSPACE_DIR}"

#############################################
# Tests finaux
#############################################
log_info "=== Tests de validation ==="

# Test Java
log_info "Test Java:"
java -version 2>&1 | head -n 1

# Test Python
log_info "Test Python:"
python3 --version

# Test PySpark
log_info "Test PySpark (import):"
python3 -c "import pyspark; print(f'PySpark version: {pyspark.__version__}')"

# Test Spark
log_info "Test Spark Shell (version):"
${SPARK_HOME}/bin/spark-shell --version 2>&1 | grep "version"

#############################################
# Résumé de l'installation
#############################################
echo ""
echo "=============================================="
log_info "🎉 Installation terminée avec succès !"
echo "=============================================="
echo ""
echo "📍 Informations importantes:"
echo "   - SPARK_HOME: ${SPARK_HOME}"
echo "   - Workspace: ${WORKSPACE_DIR}"
echo "   - Spark UI: http://localhost:4040 (quand Spark est actif)"
echo "   - Jupyter: http://localhost:8888 (à démarrer manuellement)"
echo ""
echo "🚀 Pour commencer:"
echo "   1. Recharger les variables: source ~/.bashrc"
echo "   2. Tester PySpark: pyspark"
echo "   3. Lancer le test: python3 ${WORKSPACE_DIR}/scripts/test_spark.py"
echo "   4. Lancer Jupyter: jupyter notebook --ip=0.0.0.0 --no-browser"
echo ""
echo "📚 Commandes utiles:"
echo "   - pyspark                    # Shell PySpark interactif"
echo "   - spark-shell                # Shell Scala interactif"
echo "   - spark-submit script.py     # Exécuter un script"
echo ""
echo "✅ Prochaine étape: Redémarrez votre shell ou tapez 'source ~/.bashrc'"
echo "=============================================="

log_info "=== Fin de l'installation ==="
