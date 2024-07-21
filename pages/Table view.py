import pandas as pd
import streamlit as st
from pandas.api.types import CategoricalDtype

categories={
    "top": "Top of the chest",
    "first": "Top drawer",
    "third": "Bottom drawer",
    "fridge": "Fridge",
    "floor": "Floor / elsewhere"}
categories_rev={v: k for k, v in categories.items()}

wheretype = CategoricalDtype(categories.keys(), ordered=True)
coltypes = {
    "thing": "string",
    "where": wheretype,
    "goal": "int",
    "stored": "int",
}

if "data" not in st.session_state:
    df = pd.read_csv("data.csv", dtype=coltypes)
    st.session_state["data"] = df
    st.session_state["orig_data"] = df.copy()

df = st.session_state["data"]
orig_df = st.session_state["orig_data"]

df["Where"] = df["where"].apply(lambda c: categories[c]).astype("category")

column_config = {
    "thing": st.column_config.TextColumn(
        label="Thing",
        width="medium",
        required=True,
    ),
    "Where": st.column_config.SelectboxColumn(
        label="Category",
        required=True,
    ),
    "goal": st.column_config.NumberColumn(
        label="Goal",
        required=True,
        default=1,
        min_value=0,
        step=1,
    ),
    "stored": st.column_config.NumberColumn(
        label="Stored",
        required=True,
        default=0,
        min_value=0,
        step=1,
    )
}

df = st.data_editor(
    df[["thing", "Where", "goal", "stored"]],
    num_rows="dynamic",
    height=20*35,
    hide_index=True,
    column_config=column_config)

df["where"] = df["Where"].apply(lambda c: categories_rev[c]).astype(wheretype)
df["goal"] = df["goal"].astype("int")
df["stored"] = df["stored"].astype("int")
df = df[["thing", "where", "goal", "stored"]]

if not orig_df.equals(df):
    _, middle, _ = st.columns([0.8, 1, 0.8])
    if middle.button("Save changes"):
        stored_df = pd.read_csv("data.csv", dtype=coltypes)
        if not orig_df.equals(stored_df):
            st.toast("**Cannot save: the underlying data was changed.** "
                     "Save your changes using copy/paste, then reload the page.")
        else:
            df.sort_values("where", kind="stable").to_csv("data.csv", index=False)
            del st.session_state["data"]
            st.rerun()

