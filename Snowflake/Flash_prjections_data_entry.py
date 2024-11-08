import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from snowflake.snowpark.context import get_active_session
session = get_active_session()




def get_week_range(weeks_ago=0):
  today = datetime.now().date()
  start_of_week = today - timedelta(days=today.weekday())
  target_week_start = start_of_week - timedelta(weeks=weeks_ago)
  end_of_week = target_week_start + timedelta(days=6)
  return target_week_start, end_of_week
    
def click_button():
    st.session_state.clicked = True
    st.session_state.current_page = "page1"
def on_change_egp(channel):
    if channel == "Integrated Enterprise" or channel == "Integrated Agent" or channel == "Integrated Inside":
        col1, col2 = st.columns(2)
        with col1:
            mtd_egp = st.nAumber_input("MTD EGP")
        with col2:
            projected_egp = st.number_input("Projected EGP")
        return mtd_egp,projected_egp
    else:
        col1, col2 = st.columns(2)
        with col1:
            mtd_im = st.number_input("MTD IM")
        with col2:
            projected_im = st.number_input("Projected IM")
        return mtd_im,projected_im
        
     

def page1():
    st.title("Flash Projections")
    week_options = []
    for i in range(5):
        start, end = get_week_range(i)
        week_label = f"{start:%m/%d} - {end:%m/%d}"
        week_options.append(week_label)

  # Create a selectbox for week selection
    selected_week = st.selectbox("Select Week", week_options, index=0)
    channel = st.selectbox("Budget Channel",("HPY B2B","EVO B2B","Canada","Como","HPOS Dealer","Direct Enterprise and MM",
"Direct Inside","Rock Inside no SDR","Zac M Inside","EVO ISV","FI Inside","HPY ISV","HPOS Inside","SDR","Direct Other",
"Integrated Agent","Integrated Enterprise","Integrated Inside","Payments Field","FI Field","POS Field","Payroll Field"))
    st.write("You selected:", channel)
    if channel:
            mtd, projected = on_change_egp(channel)
                    
        

    submitted = st.button("Submit")
    if submitted:
        if not channel or not mtd or not projected:
            st.warning("Fill in all the details");
        else:
            
            st.session_state.channel = channel
            st.session_state.mtd = mtd
            st.session_state.projected = projected
            st.session_state.selected_week = selected_week
            st.session_state.current_page = "page2"


def page2():
    st.title("Flash Projections Data")
    #st.write("You entered:")
    
    st.session_state.current_page = "page2"
    channel = st.session_state.channel
    mtd = st.session_state.mtd
    selected_week = st.session_state.selected_week
    projected = st.session_state.projected
    
    data = [selected_week, channel ,mtd, projected]
    data_dict = { "Selected Week": data[0],"Channel": data[1], "MTD": data[2], "Projected": data[3]}
        #st.write(data_dict)
    data1 = pd.DataFrame(data_dict, index=[0])
    
    def display_card(data1, title):
        html_content = f""" <div style="border: 1px solid #ccc; border-radius: 5px; padding: 15px; margin-bottom: 20px;">\
                <div style="background-color: black; color: white; padding: 10px; border-radius: 5px 5px 0 0;">\
                <strong>{title}</strong>\
                </div><div style="padding: 10px;">\
                <table style="width: 100%;"> """

        for i, (key, value) in enumerate(data1.items()):
            #if i % 2 == 0:
            html_content += "<tr>"
            html_content += f"<td><strong>{key.replace('_', ' ').title()}:</strong></td><td>{value}</td>"
            #if i % 2 == 1:
            html_content += "</tr>"
        html_content += """</table></div></div>"""
        st.markdown(html_content, unsafe_allow_html=True)
    if isinstance(data1, pd.DataFrame) and not data1.empty:
        data2 = data_dict
        display_card(data2, "You entered:")
        insert_query = f"insert into sandbox.akshitha.flash_goals_aug11\
                                (selected_week, MOnthdate, budget_channel,mtd_IM_EGP, projected_IM_EGP)\
                                values ('{selected_week}',CURRENT_timestamp(),'{channel}','{mtd}','{projected}') ;"
        duplicate_query = f"select * from sandbox.akshitha.flash_goals_aug11 where  \
                               budget_channel = '{channel}'and mtd_IM_EGP = '{mtd}' and projected_IM_EGP = '{projected}'"
    
        
        #re_enter = st.button("Re-enter", on_click=click_button)   
        
        #if session.sql(duplicate_query).collect():
            #st.write(session.sql(duplicate_query).collect())
            #st.warning("Duplicates: Data already exists")
            
        #if st.button("Re-enter", on_click=click_button):
            #st.write("Taking to page 1")
            #st.session_state.current_page = "page1"
            
        data1 = session.sql(insert_query).collect()
        st.success("Data inserted successfully")
        if st.button("Home", on_click=click_button):
            #st.write("Taking to page 1")
            st.session_state.current_page = "page1"
            
    
            
                #st.snow()
                
                #st.write(data1)
        #edit = st.button("Re-enter", on_click=click_button)       
    
                
    

if __name__ == "__main__":
    #st.set_page_config(page_title="My App", page_icon=":house:")

    if "current_page" not in st.session_state:
        st.session_state.current_page = "page1"

    if st.session_state.current_page == "page1":
        page1()
    elif st.session_state.current_page == "page2":
        page2()
        #
