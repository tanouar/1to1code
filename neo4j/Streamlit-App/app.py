# app.py
import streamlit as st
import streamlit.components.v1 as components
from modules.neo4j_connector import Neo4jConnector
from modules.graph_builder import build_pyvis_graph
from modules.ui_helpers import sidebar_filters

# ========================================
# Configuration Neo4j
# ========================================
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "plbconsultant"

st.set_page_config(page_title="Neo4j Graph Explorer", layout="wide")
st.title("🌐 Neo4j Graph Explorer - Interactive")

# Connexion à Neo4j
connector = Neo4jConnector(NEO4J_URI, NEO4J_USER, NEO4J_PASS)

# Récupération dynamique des labels et types de relations
all_labels = connector.get_all_labels()
all_rel_types = connector.get_all_relation_types()

# Sidebar : filtres
selected_labels, selected_rels = sidebar_filters(all_labels, all_rel_types)

# Bouton pour rafraîchir le graphe
if st.sidebar.button("🔄 Rafraîchir le graphe"):
    st.rerun()  # ⚡ Remplace st.experimental_rerun

# Récupération des nœuds et relations filtrés
nodes, relationships = connector.get_graph(labels=selected_labels, rel_types=selected_rels)

st.sidebar.markdown(f"**Nœuds récupérés :** {len(nodes)}")
st.sidebar.markdown(f"**Relations récupérées :** {len(relationships)}")

# Affichage du graphe Pyvis
if nodes:
    graph_html = build_pyvis_graph(nodes, relationships, height="750px")
    components.html(graph_html, height=750, scrolling=True)
else:
    st.warning("Aucun nœud ou relation ne correspond aux filtres sélectionnés.")

# Chemin vers ton fichier style.grass exporté depuis Neo4j Browser
STYLE_FILE = "assets/style.grass"

# Construction du graphe Pyvis
if nodes:
    graph_html = build_pyvis_graph(nodes, relationships, height="750px", style_file=STYLE_FILE)
    components.html(graph_html, height=750, scrolling=True)
else:
    st.warning("Aucun nœud ou relation ne correspond aux filtres sélectionnés.")
