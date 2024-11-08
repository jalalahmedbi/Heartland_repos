# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
import streamlit.components.v1 as components
from jinja2 import Template

st.set_page_config(layout="wide")
# Get the current credentials
session = get_active_session()

#@st.cache_data(ttl=3600)
def get_mid(mid):
    query = """
        select 1
        from sandbox.conklin.sott_tool_data
        where merchant_number = ?
        """
    data = session.sql(query, [f"{mid}"])
    return data.count() > 0

#@st.cache_data(ttl=3600)
def get_mid_dba(mid):
    query = """
        select distinct merchant_number, dba_name
        from sandbox.conklin.sott_tool_data
        where merchant_number::INT = ?
        """
    return session.sql(query, [f"{mid}"]).to_pandas()

#@st.cache_data(ttl=3600)
def get_discount_details(mid):
    query = """
        select merchant_number
            ,msk
            ,type
            ,subtype as Card_Type
            ,ORIGINAL_SOTTID
            ,ORIGINAL_RATE
            ,PRICINGACTION_SOTTID
            ,PRICINGACTION_RATE
            ,TOTAL_RATE
        from sandbox.conklin.sott_tool_data
        where type = 'Discount Rate'
        and merchant_number::INT = ?
        order by merchant_number, card_type desc
    """
    return session.sql(query, [f"{mid}"]).to_pandas()

#@st.cache_data(ttl=3600)
def get_monthlyfee_Details(mid):
    query = """
        select merchant_number
            ,msk
            ,type
            ,subtype as Fee
            ,ORIGINAL_SOTTID
            ,ORIGINAL_RATE
            ,PRICINGACTION_SOTTID
            ,PRICINGACTION_RATE
            ,TOTAL_RATE
        from sandbox.conklin.sott_tool_data
        where type = 'Monthly Fee'
        and merchant_number::INT = ?
        order by merchant_number, fee desc
    """
    return session.sql(query, [f"{mid}"]).to_pandas()

#@st.cache_data(ttl=3600)
def get_txn_details(mid):
    query = """
        select merchant_number
            ,msk
            ,type
            ,subtype as Card_Type
            ,ORIGINAL_SOTTID
            ,ORIGINAL_RATE
            ,PRICINGACTION_SOTTID
            ,PRICINGACTION_RATE
            ,TOTAL_RATE
        from sandbox.conklin.sott_tool_data
        where type in ('Authorization Fee', 'Txn Fee')
        and merchant_number:: INT = ?
        order by merchant_number, type, card_type desc
    """
    return session.sql(query, [f"{mid}"]).to_pandas()

#@st.cache_data(ttl=3600)
def get_all_details(mid):
    query = """
        select merchant_number
            ,msk
            ,type
            ,subtype
            ,ORIGINAL_SOTTID
            ,ORIGINAL_RATE
            ,PRICINGACTION_SOTTID
            ,PRICINGACTION_RATE
            ,TOTAL_RATE
        from sandbox.conklin.sott_tool_data
        where merchant_number:: INT = ?
        order by merchant_number, type, subtype desc
    """
    return session.sql(query, [f"{mid}"]).to_pandas()


# Write directly to the app
#st.title(":moneybag: SOTT Pricing Tool :moneybag:")
st.markdown("<h1 style='text-align: center;'>Pricing SOTT Tool</h1>", unsafe_allow_html=True)
#st.markdown("")
#st.markdown("")
#st.write("TBD - Pricing Sott Lookup tool")
#discount_details = get_discount_details(merchant_number)
#monthlyfee_details = get_monthlyfee_Details(merchant_number)
#txnfee_details = get_txn_details(merchant_number)
#st.write(discount_details)
#Sidebar
with st.form("Merchant filter form"):
    css="""
    <style>
    [data-testid="stForm"] {
        background: lightGrey;
    }
    </style>
    """
    st.write(css, unsafe_allow_html=True)
    #st.write("Search for or select a merchant")
    st.subheader(":blue[Merchant Pricing Lookup]")
    #mids = get_mid()
    merchant_number = st.text_input("Search for a merchant by Merchant Number")
    submitted = st.form_submit_button(":blue[Retrieve Merchant]")
    if submitted:
    #Filtering if filters are set
        if get_mid(merchant_number):
            tab1, tab2 = st.tabs(['Merchant Details', 'Download'])
            with tab1:
                #st.header("Merchant Details - Discount")
                if merchant_number:
                    discount_details = get_discount_details(merchant_number)
                    monthlyfee_details = get_monthlyfee_Details(merchant_number)
                    txnfee_details = get_txn_details(merchant_number)
                    dba = get_mid_dba(merchant_number)
                    #df = pd.DataFrame(dba)         
                    #st.header("Merchant Details")
                    #components.html(df.to_html(header=False, index=False, border=False))
                    #st.caption(f'Filtering by Merchant:') #:blue[{merchant_number} - {dba}]')
                    st.dataframe(dba, hide_index=True, width=600)
                    discount_details = discount_details[discount_details['MERCHANT_NUMBER'] == merchant_number]
                    monthlyfee_details = monthlyfee_details[monthlyfee_details['MERCHANT_NUMBER'] == merchant_number]
                    txnfee_details = txnfee_details[txnfee_details['MERCHANT_NUMBER'] == merchant_number]
                    discount_details = discount_details.style.format(
                        {
                            'MERCHANT_NUMBER': lambda x: str(x),
                            'MSK': '{:.0f}',
                            'TYPE': lambda x: str(x),
                            'CARD_TYPE': lambda x: str(x),
                            'ORIGINAL_SOTTID': lambda x: str(x),
                            'ORIGINAL_RATE': lambda x: '{:.5f}'.format(x),
                            'PRICINGACTION_SOTTID': lambda x: str(x),
                            'PRICINGACTION_RATE': lambda x: '{:.5f}'.format(x),
                            'TOTAL_RATE': lambda x: '{:.5f}'.format(x)
                        }
                    )
                    st.subheader("Discount")
                    st.dataframe(discount_details, hide_index=True, use_container_width=True)
                    
                    monthlyfee_details = monthlyfee_details.style.format(
                        {
                            'MERCHANT_NUMBER': lambda x: str(x),
                            'MSK': '{:.0f}',
                            'TYPE': lambda x: str(x),
                            'CARD_TYPE': lambda x: str(x),
                            'ORIGINAL_SOTTID': lambda x: str(x),
                            'ORIGINAL_RATE': lambda x: '${:.2f}'.format(x),
                            'PRICINGACTION_SOTTID': lambda x: str(x),
                            'PRICINGACTION_RATE': lambda x: '${:.2f}'.format(x),
                            'TOTAL_RATE': lambda x: '${:.2f}'.format(x)
                        }
                    )
                    st.subheader("Monthly Fees")
                    st.dataframe(monthlyfee_details, hide_index=True, use_container_width=True)
                    
                    txnfee_details = txnfee_details.style.format(
                        {
                            'MERCHANT_NUMBER': lambda x: str(x),
                            'MSK': '{:.0f}',
                            'TYPE': lambda x: str(x),
                            'CARD_TYPE': lambda x: str(x),
                            'ORIGINAL_SOTTID': lambda x: str(x),
                            'ORIGINAL_RATE': lambda x: '${:.2f}'.format(x),
                            'PRICINGACTION_SOTTID': lambda x: str(x),
                            'PRICINGACTION_RATE': lambda x: '${:.2f}'.format(x),
                            'TOTAL_RATE': lambda x: '${:.2f}'.format(x)
                        }
                    )
                    st.subheader("TXN Fees")
                    st.dataframe(txnfee_details,hide_index=True, use_container_width=True)
                    
            with tab2:
                if merchant_number:
                    all_details = get_all_details(merchant_number)
                    dba = get_mid_dba(merchant_number)
                    st.header("Download")
                    st.dataframe(dba, hide_index=True, width=600)
                    all_details = all_details[all_details['MERCHANT_NUMBER'] == merchant_number]
                    all_details = all_details.style.format(
                        {
                            'MERCHANT_NUMBER': lambda x: str(x),
                            'MSK': '{:.0f}',
                            'TYPE': lambda x: str(x),
                            'SUBTYPE': lambda x: str(x),
                            'ORIGINAL_SOTTID': lambda x: str(x),
                            'ORIGINAL_RATE': lambda x: '{:.5f}'.format(x),
                            'PRICINGACTION_SOTTID': lambda x: str(x),
                            'PRICINGACTION_RATE': lambda x: '{:.5f}'.format(x),
                            'TOTAL_RATE': lambda x: '{:.5f}'.format(x)
                        }
                    )
                    st.dataframe(all_details, hide_index=True, use_container_width=True)
                
        else:
            st.error("Could not find a merchant by that MID.")

