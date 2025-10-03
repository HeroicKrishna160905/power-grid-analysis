import streamlit as st
import pkg_resources
import pandas as pd

st.set_page_config(layout="wide")
st.warning("### 🔬 Environment Inspector")
st.write("""
This is a temporary diagnostic app to solve a stubborn dependency issue. 
Its purpose is to read the application's environment and report exactly which library versions are installed. 
This will tell us if Streamlit Cloud is correctly installing the packages from `requirements.txt`.
""")

if st.button("▶️ Inspect Environment", type="primary"):
    
    st.info("Reading installed packages...")

    # List of packages to check from your requirements file
    packages_to_check = [
        "pandapower",
        "pandas",
        "numpy",
        "scipy",
        "streamlit"
    ]

    installed_packages = {
        pkg: pkg_resources.get_distribution(pkg).version
        for pkg in pkg_resources.working_set.by_key
    }
    
    report_data = []
    for pkg in packages_to_check:
        if pkg in installed_packages:
            report_data.append({"Package": pkg, "Installed Version": installed_packages[pkg]})
        else:
            report_data.append({"Package": pkg, "Installed Version": "NOT FOUND"})

    st.subheader("Installed Package Versions")
    st.write("This table shows the versions that are *actually* running in the cloud environment.")
    st.dataframe(pd.DataFrame(report_data), use_container_width=True)

    st.subheader("Contents of `requirements.txt`")
    st.write("This is the `requirements.txt` file as seen by the running application.")
    try:
        with open("requirements.txt", "r") as f:
            st.code(f.read(), language="text")
    except FileNotFoundError:
        st.error("`requirements.txt` not found in the root directory!")

