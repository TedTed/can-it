import streamlit as st

desktop = st.Page("desktop.py", title="Desktop view  🖥️", icon="🥫", default=True)
mobile = st.Page("mobile.py", title="Mobile view  📱", icon="🥫")
edit = st.Page("direct_edit.py", title="Direct edit  🖊️", icon="📝")
pg = st.navigation([desktop, mobile, edit])
pg.run()
