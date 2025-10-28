# modules/graph_builder.py
from pyvis.network import Network
import re
import hashlib

def hex_to_rgba(hex_color):
    if not isinstance(hex_color, str):
        return hex_color
    s = hex_color.strip()
    m8 = re.match(r'^#([0-9a-fA-F]{8})$', s)
    m6 = re.match(r'^#([0-9a-fA-F]{6})$', s)
    if m8:
        hexa = m8.group(1)
        r = int(hexa[0:2], 16)
        g = int(hexa[2:4], 16)
        b = int(hexa[4:6], 16)
        a = int(hexa[6:8], 16) / 255
        return f"rgba({r}, {g}, {b}, {a:.2f})"
    if m6:
        return s
    return s

def clean_value(raw):
    if raw is None:
        return raw
    v = raw.strip()
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        v = v[1:-1]
    return v.strip()

def parse_style_grass(file_path):
    label_styles = {}
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    node_blocks = re.findall(r'(node(?:\.\*|(?:\.[A-Za-z0-9_]+))?\s*\{.*?\})', content, re.DOTALL)
    for block in node_blocks:
        m = re.match(r'node(?:\.([A-Za-z0-9_]+)|\.\*)?\s*\{', block)
        label_raw = m.group(1) if m and m.group(1) else "*"
        label = label_raw.lower()
        props = {}
        for k, v in re.findall(r'([A-Za-z0-9_-]+)\s*:\s*([^;]+);', block):
            props[k] = clean_value(v)
        label_styles[label] = props

    rel_blocks = re.findall(r'(relationship\s*\{.*?\})', content, re.DOTALL)
    for block in rel_blocks:
        props = {}
        for k, v in re.findall(r'([A-Za-z0-9_-]+)\s*:\s*([^;]+);', block):
            props[k] = clean_value(v)
        label_styles["relationship"] = props

    return label_styles

def apply_caption_template(caption_template, node_props):
    if not caption_template:
        return None
    tpl = caption_template
    def repl(match):
        key = match.group(1)
        return str(node_props.get(key, ""))
    tpl = re.sub(r'\{([^}]+)\}', repl, tpl)
    return tpl

def _to_int_px(value, fallback=20):
    if not value:
        return fallback
    v = str(value).strip()
    m = re.match(r'(\d+)', v)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            return fallback
    return fallback

def color_from_label(label):
    h = hashlib.md5(label.encode("utf-8")).hexdigest()
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return f"rgb({r},{g},{b})"

def _extract_node_labels(node):
    for key in ("label", "labels"):
        if key in node:
            val = node.get(key)
            if val is None:
                return []
            if isinstance(val, list):
                return [str(x) for x in val if x is not None]
            return [str(val)]
    return []

def build_pyvis_graph(nodes, relationships, height="600px", style_file=None, label_map=None, debug=False):
    net = Network(height=height, width="100%", directed=True)
    net.force_atlas_2based()

    label_styles = {}
    if style_file:
        label_styles = parse_style_grass(style_file)

    label_map = {k.lower(): v.lower() for k, v in (label_map or {}).items()}

    debug_list = []

    for node in nodes:
        raw_label_list = _extract_node_labels(node)
        raw_lower = [l.lower() for l in raw_label_list]

        # Appliquer mapping si fourni
        mapped = []
        for l in raw_lower:
            mapped.append(label_map.get(l, l))
        chosen_label = None
        for l in mapped:
            if l in label_styles:
                chosen_label = l
                break
        if chosen_label is None and "*" in label_styles:
            chosen_label = "*"

        style = label_styles.get(chosen_label, {})

        # Couleurs
        if style and "color" in style:
            bg_color = hex_to_rgba(style.get("color"))
            border_color = hex_to_rgba(style.get("border-color", style.get("border-color", "#000000")))
        else:
            # génération automatique si pas de style spécifique
            label_for_color = raw_lower[0] if raw_lower else str(node.get("id"))
            bg_color = color_from_label(label_for_color)
            border_color = bg_color

        text_color_internal = style.get("text-color-internal") or style.get("text-color") or "#000000"

        # Taille (diameter) et bord
        size = _to_int_px(style.get("diameter", None), fallback=40)  # taille par défaut plus grande pour le texte
        border_width = _to_int_px(style.get("border-width", None), fallback=2)

        # Caption : privilégier le champ 'name' ou template du .grass
        caption_template = style.get("caption") or style.get("defaultCaption")
        caption = None
        # si le .grass propose <id> ou autres tokens entre chevrons, on laisse littéral; ici on veut afficher name
        if caption_template:
            caption = apply_caption_template(caption_template, node)
        # priorité: champ name > title > id > caption_template
        caption = node.get("name") or node.get("title") or caption or str(node.get("id"))

        # Ajuster police: taille en fonction du diamètre
        # font.size correspond à px dans vis.js
        font_size = max(10, int(size / 3))
        font_color = text_color_internal

        # Créer l'argument color pour vis.js (background + border)
        color_arg = {
            "background": bg_color,
            "border": border_color,
            "highlight": {"background": bg_color, "border": border_color},
            "hover": {"background": bg_color, "border": border_color}
        }

        net.add_node(
            node["id"],
            label=caption,
            title="<br>".join([f"{k}: {v}" for k, v in node.items() if k not in ("id", "label", "labels")]),
            color=color_arg,
            size=size,
            borderWidth=border_width,
            font={"color": font_color, "size": font_size, "face": "Arial", "align": "center"}
        )

        debug_list.append({
            "id": node.get("id"),
            "raw_labels": raw_label_list,
            "chosen_label": chosen_label,
            "caption": caption,
            "bg_color": bg_color,
            "border_color": border_color,
            "size": size,
            "font_size": font_size
        })

    # Relations
    rel_style = label_styles.get("relationship", {})
    rel_color = hex_to_rgba(rel_style.get("color", "#A5ABB6"))
    rel_width = _to_int_px(rel_style.get("shaft-width", None), fallback=2)
    rel_caption_template = rel_style.get("caption")

    for rel in relationships:
        caption = rel_caption_template or rel.get("type", "")
        if isinstance(caption, str) and "<type>" in caption:
            caption = caption.replace("<type>", rel.get("type", ""))
        net.add_edge(
            rel["source"],
            rel["target"],
            label=caption,
            color=rel_color,
            width=rel_width
        )

    # Options : shape circle et police par défaut
    net.set_options("""
    var options = {
      "nodes": {
        "shape": "circle",
        "font": {"multi": false, "face": "Arial"}
      },
      "edges": {"arrows": {"to": {"enabled": true}}},
      "physics": {"forceAtlas2Based": {"gravitationalConstant": -50}}
    }
    """)
    html = net.generate_html()
    if debug:
        return {"html": html, "debug": debug_list}
    return html
