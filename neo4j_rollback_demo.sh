#!/bin/bash

# ============================================
# 🧠 Démonstration : Transaction & Rollback Neo4j
# Base : Neo4j Community Edition
# Auteur : PLB Consultant
# ============================================

# Configuration
NEO4J_USER="neo4j"
NEO4J_PASS="plbconsultant"
NEO4J_URL="http://localhost:7474/db/neo4j"

# Fonction utilitaire pour séparer les étapes visuellement
separator() {
  echo
  echo "=============================================="
  echo "➡️  $1"
  echo "=============================================="
  echo
}

# Étape 1 — Vérification de l'état initial
separator "1️⃣  Vérification du nœud Hulk"
curl -s -u "$NEO4J_USER:$NEO4J_PASS" \
  -H "Content-Type: application/json" \
  -X POST "$NEO4J_URL/tx/commit" \
  -d '{"statements":[{"statement":"MATCH (c:Character {name:\"Hulk\"}) RETURN c"}]}' \
| jq

# Étape 2 — Ouverture d'une transaction et modification temporaire
separator "2️⃣  Création d'une transaction et modification du nom de Hulk"

RESPONSE=$(curl -s -D - -u "$NEO4J_USER:$NEO4J_PASS" \
  -H "Content-Type: application/json" \
  -X POST "$NEO4J_URL/tx" \
  -d '{"statements":[{"statement":"MATCH (c:Character {name:\"Hulk\"}) SET c.name=\"Dr. Banner\" RETURN c"}]}')

# Extraction de l'ID de transaction depuis les en-têtes
TX_ID=$(echo "$RESPONSE" | grep -i "Location:" | sed 's/.*\/tx\/\([0-9]*\).*/\1/' | tr -d '\r')

echo "🔢 ID de la transaction ouverte : $TX_ID"
echo "$RESPONSE" | tail -n +$(($(echo "$RESPONSE" | grep -n '^{' | cut -d: -f1 | head -1))) | jq

# Étape 3 — Rollback immédiat
separator "3️⃣  Annulation de la transaction (ROLLBACK)"
curl -s -u "$NEO4J_USER:$NEO4J_PASS" \
  -X DELETE "$NEO4J_URL/tx/$TX_ID" \
| jq

# Étape 4 — Vérification finale après rollback
separator "4️⃣  Vérification après rollback"
curl -s -u "$NEO4J_USER:$NEO4J_PASS" \
  -H "Content-Type: application/json" \
  -X POST "$NEO4J_URL/tx/commit" \
  -d '{"statements":[{"statement":"MATCH (c:Character{name:\"Hulk\"}) RETURN c.name"}]}' \
| jq

echo
echo "✅ Démonstration terminée : le nom du nœud est resté 'Hulk' (rollback réussi)"
echo
