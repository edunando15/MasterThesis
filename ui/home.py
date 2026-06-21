import streamlit as st

st.set_page_config(page_title="IoT Deployer", page_icon="📁")

st.title("Upload data & choose target IoT platform")

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "target_platform" not in st.session_state:
    st.session_state.target_platform = None

uploaded = st.file_uploader(
    "Upload a turtle (TTL) file",
    type=["ttl"],
    help="Upload the mapping/export file you want to convert to the target IoT platform."
)
if uploaded is not None:
    st.session_state.uploaded_file = uploaded
    st.success(f"Uploaded: {uploaded.name}")

platform = st.selectbox(
    "Select target IoT platform",
    ["Select...", "ThingsBoard", "CustomPlatformA", "CustomPlatformB"],
    index=0
)
if platform != "Select...":
    st.session_state.target_platform = platform

st.write("---")
st.write("Navigation:")
st.write("Use the sidebar (top-left ≡) to open other pages, or go to the 'Transform' page.")