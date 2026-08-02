import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "")))
import streamlit as st
from graph_db.graph_db_helper import upload_to_graphdb
from dotenv import load_dotenv, set_key

ENV_PATH = ".env"
load_dotenv(ENV_PATH)

st.set_page_config(page_title="IoT Deployer", page_icon="📁")
st.title("Upload data & choose target IoT platform")

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "target_platform" not in st.session_state:
    st.session_state.target_platform = None

uploaded = st.file_uploader(
    "Upload a turtle (TTL) file",
    type=["ttl"],
    help="Upload the BIM file you want to deploy on the target IoT platform."
)

if uploaded is not None and st.session_state.uploaded_file != uploaded.name:
    with st.spinner("Uploading to GraphDB..."):
        file_bytes = uploaded.getvalue()
        upload_to_graphdb(file_bytes)
    st.session_state.uploaded_file = uploaded.name
    st.success(f"Uploaded and synchronised: {uploaded.name}")

platform = st.selectbox(
    "Select target IoT platform",
    ["Select...", "ThingsBoard", "OpenRemote"],
    index=0
)

if platform != "Select...":
    st.session_state.target_platform = platform

    st.write("---")
    st.subheader("Environment Configuration")
    with st.form("env_config_form"):
        st.write("**GraphDB Parameters**")
        gdb_url = st.text_input("GraphDB URL", value=os.getenv("GRAPHDB_URL"))
        gdb_repo = st.text_input("GraphDB Repository", value=os.getenv("GRAPHDB_REPOSITORY"))

        tb_url, tb_user, tb_pass = None, None, None
        or_url, or_user, or_pass, or_realm = None, None, None, None

        if platform == "ThingsBoard":
            st.write("**ThingsBoard Parameters**")
            tb_url = st.text_input("URL", value=os.getenv("THINGSBOARD_URL"))
            tb_user = st.text_input("Username", value=os.getenv("THINGSBOARD_USERNAME"))
            tb_pass = st.text_input("Password", value=os.getenv("THINGSBOARD_PASSWORD"), type="password")

        elif platform == "OpenRemote":
            st.write("**OpenRemote Parameters**")
            or_url = st.text_input("URL", value=os.getenv("OPENREMOTE_URL"))
            or_user = st.text_input("Username", value=os.getenv("OPENREMOTE_USERNAME"))
            or_pass = st.text_input("Password", value=os.getenv("OPENREMOTE_PASSWORD"), type="password")
            or_realm = st.text_input("Realm", value=os.getenv("OPENREMOTE_REALM"))

        submit = st.form_submit_button("Save configuration")

        if submit:
            env_updates = {
                "GRAPHDB_URL": gdb_url,
                "GRAPHDB_REPOSITORY": gdb_repo
            }
            if platform == "ThingsBoard":
                env_updates["THINGSBOARD_URL"] = tb_url
                env_updates["THINGSBOARD_USERNAME"] = tb_user
                env_updates["THINGSBOARD_PASSWORD"] = tb_pass
            elif platform == "OpenRemote":
                env_updates["OPENREMOTE_URL"] = or_url
                env_updates["OPENREMOTE_USERNAME"] = or_user
                env_updates["OPENREMOTE_PASSWORD"] = or_pass
                env_updates["OPENREMOTE_REALM"] = or_realm

            for key, val in env_updates.items():
                if val is not None:
                    set_key(ENV_PATH, key, val)
                    os.environ[key] = val

            st.success("Environment variables successfully updated.")

st.write("---")
st.write("Navigation:")
st.write("Use the sidebar (top-left ≡) to open other pages, or go to the 'Transform' page.")