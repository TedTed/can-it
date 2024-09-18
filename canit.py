import pandas as pd
import streamlit as st

def view(desktop):
    st.markdown("""
    <style>
        span[data-testid="stHeaderActionElements"] > a:first-child {
            display: none !important;
        }
        h3 {
            text-align: center;
        }
        h5 {
            text-align: center;
        }
        div[data-testid="stMarkdownContainer"] > p {
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)

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

    if "alphabetical" not in st.session_state:
        st.session_state["alphabetical"] = False

    # Search logic
    def search():
        st.session_state["missing"] = False
        st.session_state["category"] = None
        reload_view()
    def reset():
        del st.session_state["search"]
        del st.session_state["missing"]
        del st.session_state["category"]

    options = st.container(border=True) if desktop else st.expander("Search & filter options")

    # Displaying search options
    left, middle, right = options.columns([5.5, 1, 1])
    left.text_input(
        "Search",
        key="search",
        placeholder="Search for a thing…",
        label_visibility="collapsed",
        on_change=search)
    middle.button("Search", on_click=search, use_container_width=True)
    right.button("Reset", on_click=reset, use_container_width=True)

    # Displaying filter options
    left, middle, right = options.columns([3, 2.5, 2], vertical_alignment="center")
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
    middle.checkbox(
        "Only show missing things",
        key="missing",
        on_change=reload_view)
    right.checkbox(
        "Sort alphabetically",
        key="alphabetical",
        on_change=reload_view)

    filtered_df = df[st.session_state["filter"]]
    if st.session_state["alphabetical"]:
        filtered_df = filtered_df.sort_values("thing")

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
    cols = [2.5, 2.5, 2.5]
    if desktop:
        thing, amount, addremove = st.columns(cols)
        thing.subheader("Thing")
        amount.subheader("Goal/stored/diff")
        addremove.subheader("Add/remove")

    # Table
    first = True
    if filtered_df.empty:
        st.header("Nothing is missing   🥳")
    for i, row in filtered_df.iterrows():
        c = st.container()
        thing, amount, addremove = (
            st.columns(cols, vertical_alignment="center") if desktop
            else (c, c, st))
        # Ingredient name and location (for mobile)
        location = categories[row['where']]
        if desktop:
            thing.markdown(f"**{row['thing']}**")
        else:
            thing.markdown(f"##### {row['thing']}")
            thing.markdown(f"({location})")
        # Add/remove buttons
        add, remove = addremove.columns(2)
        if add.button(" +1 ", key=f"add_{i}", on_click=keep_view, use_container_width=True):
            add_one(i)
        if remove.button(" -1 ", key=f"remove_{i}", on_click=keep_view, use_container_width=True):
            remove_one(i)
        # Amount
        g = row['goal']
        s = df.at[i, 'stored'] # and not row['stored'], which is a copy
        d = s-row['goal']
        text = ""
        if desktop:
            text += f"**{g}  /  {s}  /  "
        else:
            text += f"**Need {g}, got {s}, diff  "
        if d < 0:
            text += f":red-background[{d}   😱]"
        elif d > 0:
            text += f":orange-background[{d}   🤔]"
        else:
            text += f":green-background[0  🎉]"
        text += "**"
        amount.markdown(text)

    df.to_csv("data.csv", index=False)
