import streamlit as st
import os

st.set_page_config(
    page_title="visualisaties",
    page_icon= "📊"
    )

st.title("visualisaties 📊")

if os.path.exists("Omloopplanning_Gantt.png"):
    st.image('Omloopplanning_Gantt.png')




delete = st.button('Delete Data')

if delete:
    
    if os.path.exists("Omloopplanning_Gantt.png"):
        os.remove("Omloopplanning_Gantt.png")

