import streamlit as st
import pandas as pd

st.set_page_config(page_title="Transform", page_icon="🔁")

st.title("Transform / Map to target platform")

uploaded = st.session_state.get("uploaded_file", None)
platform = st.session_state.get("target_platform", None)

if uploaded is None:
    st.warning("No file uploaded yet. Go to the Home page and upload a file.")
else:
    st.write(f"Uploaded file: **{uploaded.name}**")
    # Try to display a preview for common types
    file_name = uploaded.name.lower()
    try:
        if file_name.endswith(".csv"):
            df = pd.read_csv(uploaded)
            st.dataframe(df.head())
        elif file_name.endswith(".json"):
            uploaded.seek(0)
            data = uploaded.read().decode("utf-8")
            st.json(data)
        elif file_name.endswith(".ttl") or file_name.endswith(".txt"):
            uploaded.seek(0)
            text = uploaded.read().decode("utf-8")
            st.code(text[:1000])
        else:
            st.info("Preview not available for this file type.")
    except Exception as e:
        st.error(f"Could not preview file: {e}")

if not platform:
    st.info("No target platform selected. Choose it on the Home page.")
else:
    st.write(f"Target platform: **{platform}**")

# Example: a button to run a (placeholder) mapping action
if st.button("Run mapping"):
    if uploaded is None or not platform:
        st.error("Please upload a file and select a target platform first.")
    else:
        st.info(f"Running mapping for {uploaded.name} -> {platform} ...")
        # Here you'd call your transformation logic (not implemented in this example)
        st.success("Mapping complete (example).")