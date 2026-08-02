import streamlit as st
import os
from dotenv import load_dotenv
from deployment.thingsboard_deployment import execute_thingsboard_deployment
from deployment.openremote_deployment import execute_openremote_deployment

load_dotenv(override=True)

st.set_page_config(page_title="Transform", page_icon="🔁")
st.title("Transform / Map to target platform")

uploaded = st.session_state.get("uploaded_file", None)
platform = st.session_state.get("target_platform", None)

if uploaded is None:
    st.warning("No file uploaded yet. Go to the Home page and upload a file.")
elif not platform or platform == "Select...":
    st.warning("Please select a target platform first in the home page.")
else:
    st.write(f"Uploaded file: **{uploaded}**")
    file_name = uploaded.lower()
    if st.button("Run deployment"):
        graphdb_url = os.getenv("GRAPHDB_URL")
        graphdb_repository = os.getenv("GRAPHDB_REPOSITORY")
        os.makedirs("data", exist_ok=True)
        if platform == "ThingsBoard":
            with st.spinner("Executing ThingsBoard extraction and deployment..."):
                execute_thingsboard_deployment()
                st.success("ThingsBoard deployment complete.")

        elif platform == "OpenRemote":
            with st.spinner("Executing OpenRemote extraction and deployment..."):
                execute_openremote_deployment()
                st.success("OpenRemote deployment complete.")