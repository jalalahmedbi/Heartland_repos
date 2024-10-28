# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
import json

session = get_active_session()

# Write directly to the app
st.title("Payroll Risk Managment - Fraud Cases")
st.write(
    """Data Entry form for Payroll Fraud Cases displayed on the
    [Risk & Banking Metrics](https://lookerstudio.google.com/reporting/a62e8aa5-3672-4f12-a0ff-dabeba8e1dd3/page/OW28D)
    Looker Report"""
)

with st.form ("fraud_Case", clear_on_submit=True):
    st.write("Enter fraud cases here:")
    
    clientID = st.text_input(label="Client ID",max_chars=25)
    clientName = st.text_input(label="Client Name", max_chars=200)
    fraudAmount = st.number_input(label="Amount", min_value=0.00)
    fraudDate = st.date_input(label="Date", format="MM/DD/YYYY")
    location = st.selectbox("Location", ("A", "B", "C"),index=2)   
    created_dataframe = session.sql(f"""select distinct 
                                            case when lastname = '' then 'SPA NOT IN LIST' else upper(lastname || ', ' || firstname) end as NAME
                                            , case when lastname ='' then 0 else personoid end as ID 
                                            , lastname
                                        from bi.sales.employees 
                                        where lastname not in ( '.','..','.com') 
                                        order by LASTNAME;""")
    rep_selectbox_list = created_dataframe.to_pandas()

    values = rep_selectbox_list['NAME'].tolist()
    options = rep_selectbox_list['ID'].tolist()
    dic = dict(zip(options,values))

    salesRep = st.selectbox('Sales Rep',options=options, format_func=lambda x: dic[x], placeholder="Select a Sales Rep")
    bank = st.text_input(label='Bank', max_chars=100)
    comments = st.text_area(label="Comments", max_chars=2000)
    
    submitted = st.form_submit_button("Submit")
    
    if submitted:

        if not clientID:
            clientID = 'null' 
        
        if not clientName:
            clientName = 'null'
        else:
            clientName = clientName.replace("'", "''")

        if not bank:
            bank = 'null'
        else:
            bank=bank.replace("'", "''")

        if not comments:
            comments='null'
        else:
            comments=comments.replace("'", "''")
           
        try:
            session.sql(f"""INSERT INTO bi.payroll.payroll_risk_fraud_cases 
                (CLIENT_ID, CLIENT_NAME,FRAUD_AMOUNT,fraud_Date,Location, sales_rep_personoid,bank,comments,updated_Timestamp) 
                VALUES ('{clientID}', '{clientName}',{fraudAmount},'{fraudDate}','{location}',{salesRep},'{bank}','{comments}', cast(convert_timezone('US/Central',current_timestamp()) as timestamp(0)))""").collect()
            st.success('Success!', icon="✅")
            
        except Exception as e:
            st.error(f"This row was not inserted. Please contact BI with the following information: \n\r ERROR - {e}",icon='🚨')

created_dataframe = session.sql("""select p.client_ID as "Client ID"
                                    , p.Client_Name as "Client Name"
                                    , p.Fraud_Amount as "Amount"
                                    , p.Fraud_Date as "Date"
                                    , P.Location as "Location"
                                    , e.lastname || ', ' || e.firstname as "Sales Rep"
                                    , p.bank as "Bank"
                                    , p.comments as "Comments"
                                from bi.payroll.payroll_risk_fraud_cases as P
                                LEFT OUTER JOIN bi.sales.employees as e
                                on p.sales_rep_personoid = e.personoid
                                ORDER BY updated_timestamp desc""")

queried_data = created_dataframe.to_pandas()

st.subheader("Submitted fraud data")
st.dataframe(queried_data,width=2000)
