import pandas as pd
import streamlit as st

def main():
    if "data" not in st.session_state:
        st.session_state["data"] = pd.read_csv("data.csv")
    df = st.session_state["data"]

    # Initializing whether to reload the view
    if "reload" not in st.session_state:
        st.session_state["reload"] = True
    def reload_view(): st.session_state["reload"] = True
    def keep_view(): st.session_state["reload"] = False

    # Initializing filter options
    if "search" not in st.session_state:
        st.session_state["search"] = ""
    if "category" not in st.session_state:
        st.session_state["category"] = None
    if "missing" not in st.session_state:
        st.session_state["missing"] = True

    # Creating filter
    if st.session_state["reload"]:
        st.session_state["filter"] = pd.Series(True, index=df.index)
        if st.session_state["missing"]:
            st.session_state["filter"] &= df["goal"] > df["stored"]
        if st.session_state["category"]:
            st.session_state["filter"] &= df["where"] == st.session_state["category"]
        if st.session_state["search"]:
            st.session_state["filter"] &= df["thing"].str.contains(st.session_state["search"], case=False)

    # Search
    left, middle, right = st.columns([6, 1, 1])
    def search():
        st.session_state["missing"] = False
        st.session_state["category"] = None
        reload_view()
    def reset():
        del st.session_state["search"]
        del st.session_state["missing"]
        del st.session_state["category"]
    left.text_input(
        "Search",
        key="search",
        placeholder="Search for a thing…",
        label_visibility="collapsed",
        on_change=search)
    middle.button("Search", on_click=search)
    right.button("Reset", on_click=reset)

    # Displaying filter options
    left, right = st.columns([2, 1])
    categories={
        "top": "Top of the chest",
        "first": "Top drawer",
        "third": "Bottom drawer",
        "fridge": "Fridge",
        "floor": "Floor / elsewhere"}
    left.selectbox(
        "Filter by category",
        tuple(categories.keys()),
        key="category",
        index=None,
        placeholder="Filter by category…",
        label_visibility="collapsed",
        format_func = lambda code: categories[code],
        on_change=reload_view)

    def update_missing():
        st.session_state["missing"] = not st.session_state["missing"]
        update_filter()

    right.checkbox(
        "Only show missing items",
        key="missing",
        on_change=reload_view)

    view = df[st.session_state["filter"]]


    # Editing logic
    def add_one(i):
        df.at[i, "stored"] += 1

    def remove_one(i):
        v = df.at[i, "stored"]
        if v == 0:
            st.toast(f"**Can't remove any more of '{df.at[i, 'thing']}', value is 0!**")
            return
        df.at[i, "stored"] -= 1

    # Header
    headercols = [3, 2.5, 2]
    thing, amount, addremove = st.columns(headercols)
    thing.subheader("Thing")
    amount.subheader("Goal/stored/diff")
    addremove.subheader("Add/remove")

    # Table
    first = True
    #cols = [3, 1, 1, 1, 1, 1]
    cols = headercols
    if view.empty:
        st.header("Nothing is missing   🥳")
    for i, row in view.iterrows():
        thing, amount, addremove = st.columns(cols)
        # Ingredient name
        thing.write(row["thing"])
        # Add/remove buttons
        add, remove = addremove.columns(2)
        if add.button(" +1 ", key=f"add_{i}", on_click=keep_view):
            add_one(i)
        if remove.button(" -1 ", key=f"remove_{i}", on_click=keep_view):
            remove_one(i)
        # Amount
        text = f"##### {row['goal']}"
        s = df.at[i, 'stored'] # and not row['stored'], which is a copy
        text += f"  /  {s}  /  "
        d = s-row['goal']
        if d < 0:
            text += f":red-background[{d}   😱]"
        elif d > 0:
            text += f":orange-background[{d}   🤔]"
        else:
            text += f":green-background[0  🎉]"
        amount.markdown(text)


    df.to_csv("data.csv", index=False)

if __name__ == "__main__":
    main()
