import pandas as pd
import json
import streamlit as st
from snowflake.snowpark import Session
import time
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark import Session


if 'snowflake_connection' not in st.session_state:
    session = get_active_session()
else:
    session = get_active_session()

st.set_page_config(layout="centered", page_title="Data Editor", page_icon="🧮")
st.title("VP Goals ❄️")

def get_dataset():
    # load messages df
    df = session.table("test_goals")

    return df

dataset = get_dataset()

# This doesn't appear to work for any data type other than VARCHAR.  Date, DateTime, Number, etc blows up the code
with st.form("data_editor_form"):
    st.caption("Edit the dataframe below")
    edited = st.data_editor(dataset, use_container_width=True, num_rows="dynamic")
    submit_button = st.form_submit_button("Submit")

if submit_button:
    try:
        #Note the quote_identifiers argument for case insensitivity
        session.write_pandas(edited, "VP_GOALS", overwrite=True, quote_identifiers=False)
        st.success("Table updated")
        time.sleep(5)
    except:
        st.warning("Error updating table")
    #display success message for 5 seconds and update the table to reflect what is in Snowflake
    st.experimental_rerun()