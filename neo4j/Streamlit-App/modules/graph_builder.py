# modules/graph_builder.py
from pyvis.network import Network
import re

def parse_style_grass(file_path):
    """
    Parse le fichier style.grass pour associer labels -> couleurs
    Retour : dict { label: couleur }
    """
    label_colors = {}
    with open(file_path, "r") as f:
        content = f.read()
    matches = re.findall(r'node\s*\{\s*:label\s*"(.+?)".+?:color\s*"(.+?)"', content, re.DOTALL)
    for label, color in matches:
        label_colors[label] = color
    return label_colors

def build_pyvis_graph(nodes, relationships, height="600px", style_file=None):
    """
    Construit un graphe Pyvis à partir de nodes et relations
    """
    net = Network(height=height, width="100%", directed=True)
    net.force_atlas_2based()

    # Couleurs par label
    label_colors = {}
    if style_file:
        label_colors = parse_style_grass(style_file)

    # Ajout des nœuds
    for node in nodes:
        label = node.get("label", "")
        color = label_colors.get(label, "#97C2FC")  # couleur par défaut
        title = "<br>".join([f"{k}: {v}" for k, v in node.items() if k not in ("id", "label")])
        net.add_node(node["id"], label=label, title=title, color=color)

    # Ajout des relations
    for rel in relationships:
        net.add_edge(rel["source"], rel["target"], label=rel.get("type", ""))

    # Options graphiques
    net.set_options("""
    var options = {
      "nodes": {"shape": "dot", "size": 20},
      "edges": {"arrows": {"to": {"enabled": true}}},
      "physics": {"forceAtlas2Based": {"gravitationalConstant": -50}}
    }
    """)
    return net.generate_html()
