import pandas as pd
import streamlit as st
from pandas.api.types import CategoricalDtype

locations = ["top", "first", "third", "fridge", "floor"]
location_names={
    "top": "Top of the chest",
    "first": "Top drawer",
    "third": "Bottom drawer",
    "fridge": "Fridge",
    "floor": "Floor / elsewhere"}

if "data" not in st.session_state:
    st.session_state["data"] = pd.read_csv("data.csv")
df = st.session_state["data"]

if "current" not in st.session_state:
    st.session_state["current"] = -1

def validate(thing, where, need, got):
    if "," in thing:
        st.error("Commas are forbidden in things")
        return False
    if where not in locations:
        st.error("Location invalid. (How did this happen? Tell Damien.)")
        return False
    if need < 1:
        st.error("Minimum required value is 1. (How did this happen? Tell Damien.)")
        return False
    if got < 0:
        st.error("Minimum stored value is 0. (How did this happen? Tell Damien.)")
        return False
    return True

for i, row in df.iterrows():
    left, middle, right = st.columns([4, 1, 1], vertical_alignment="center")
    left.markdown(f"**{row['thing']}** ({location_names[row['where']]}): need {row['goal']}, got {row['stored']}")
    if middle.button("Edit", key=f"add_{i}", use_container_width=True):
        st.session_state["current"] = i
    if st.session_state["current"] == i:
        with st.form(f"form_{i}"):
            thing = st.text_input(
                label="Thing", value=row['thing'], key=f"thing_{i}")
            where = st.selectbox(
                "Where",
                options=locations,
                index=locations.index(row['where']),
                format_func=lambda loc: location_names[loc],
                key=f"where_{i}")
            need = st.number_input(
                "Need", value=row['goal'], min_value=1, key=f"goal_{i}")
            got = st.number_input(
                "Got", value=row['stored'], min_value=0, key=f"stored_{i}")
            if st.form_submit_button("Save", use_container_width=True) and validate(thing, where, need, got):
                st.session_state["data"].at[i, "thing"] = thing
                st.session_state["data"].at[i, "where"] = where
                st.session_state["data"].at[i, "goal"] = need
                st.session_state["data"].at[i, "stored"] = got
                st.session_state["current"] = -1
                st.rerun()
        pass
    if right.button("Delete", key=f"delete_{i}", use_container_width=True):
        df.drop(i, inplace=True)
        st.rerun()

if st.button("Add new", key="new", use_container_width=True):
    st.session_state["current"] = "new"
if st.session_state["current"] == "new":
    with st.form(f"form_new"):
        thing = st.text_input(
            label="Thing", key=f"thing_new")
        where = st.selectbox(
            "Where",
            options=locations,
            index=None,
            format_func=lambda loc: location_names[loc],
            key=f"where_new")
        need = st.number_input(
            "Need", value=1, min_value=1, key=f"goal_new")
        got = st.number_input(
            "Got", value=0, min_value=0, key=f"stored_new")
        if st.form_submit_button("Save", use_container_width=True) and validate(thing, where, need, got):
            st.session_state["data"] = pd.concat(
                [df, pd.DataFrame([[thing, where, need, got]], columns=df.columns)],
                ignore_index=True)
            st.session_state["current"] = -1
            st.rerun()

df.to_csv("data.csv", index=False)
