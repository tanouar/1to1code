# modules/ui_helpers.py
import streamlit as st

def sidebar_filters(all_labels, all_rel_types):
    st.sidebar.header("Filtres du graphe")
    selected_labels = st.sidebar.multiselect(
        "Sélectionnez les labels des nœuds",
        options=all_labels,
        default=all_labels
    )
    selected_rels = st.sidebar.multiselect(
        "Sélectionnez les types de relations",
        options=all_rel_types,
        default=all_rel_types
    )
    return selected_labels, selected_rels
