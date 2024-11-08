# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark import functions as F
session = get_active_session() 
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt



customer_list = session.table('sandbox.meghana.CALL_TRANSCRIPTS').select('customer').distinct().toPandas()

with st.sidebar:
    customer = st.selectbox("customer", customer_list, key='customer_name', placeholder="Start Typing Customer Name",)



tab1, tab2= st.tabs(["Call Transcripts", "Sentiment Analysis"])

with tab1:
#List of unique customer_ids 
    #customer = st.selectbox("customer", customer_list, key='customer_name', placeholder="Start Typing Customer Name",)

    last_5_call_summary = session.sql(f"""
        select snowflake.cortex.complete(
        'mixtral-8x7b',
        concat( 
            'Answer the question based on the context. Do not include citations','Context: ',
            (
            select array_agg(*)::varchar from (
                select CONCAT(date_created, TRANSLATION_MIXTRAL_COMPLETE) 
                from sandbox.meghana.CALL_TRANSCRIPTS
                WHERE customer = {customer}
                ORDER BY DATE_CREATED DESC
                LIMIT 5
                )
            ),
            'Question: ', 
             'Provide me with a summary of all the calls from this customer including the date in one sentence',
            'Answer: '
        )
    ) as last_5_call_summary""").collect()
    
    
    
    
    st.header("Customer Call transcript Dashboard")

  
    # filter down to the selected customer only on calls and customer data
    #customer = session.table('sandbox.meghana.CALL_TRANSCRIPTS').filter(F.col('customer')==st.session_state.customer_name).to_pandas()
    st.write('<p style="font-size:28px; color:red;"></p>',
             last_5_call_summary[0],
             unsafe_allow_html=True)
   
    
    
    #defining the slide window 
    num_chunks = 5
    slide_window = 7
    

    # #Define the configuration options like models, checkbox and buttons
    def config_options():
        
        st.selectbox('Select your model:',('mixtral-8x7b',
                                                'mistral-7b',
                                               'llama2-70b-chat',
                                               'gemma-7b',
                                                  # 'reka-flash',
                                                  # 'reka-core',
                                                   # 'mistral-large',
                                                   # 'snowflake-arctic',
                                                    # 'llama3-70b',
                                                   # 'llama3-8b',
                                                  ),key="model_name")
        col1, col2 = st.columns(2)
        col1.checkbox('Do you want that I remember the chat history?', key="use_chat_history", value = True)
        col2.button("Start Over", key="clear_conversation")
    
    
    
    
    
    # #to clear the conversation 
    def init_messages():
        # Initialize chat history
        if st.session_state.clear_conversation or "messages" not in st.session_state:
            st.session_state.messages = []

        
    def get_similar_chunks (question):
        cmd = f"""
            with results as
            (SELECT 
               VECTOR_l2_DISTANCE(m.vec,
                        snowflake.cortex.embed_text_768('e5-base-v2', ?)) as distance,
               TRANSLATION_MIXTRAL_COMPLETE, 
               date_created
            from SANDBOX.MEGHANA.CALL_TRANSCRIPTS m
            WHERE customer = {customer}
            order by distance asc
            limit 5)
            select concat(date_created,TRANSLATION_MIXTRAL_COMPLETE) as chunk from results
        """
        
        df_chunks = session.sql(cmd, params=[question, num_chunks]).to_pandas()       
    
        df_chunks_lenght = len(df_chunks) -1
    
        similar_chunks = ""
        for i in range (0, df_chunks_lenght):
            similar_chunks += df_chunks._get_value(i, 'CHUNK')
    
        similar_chunks = similar_chunks.replace("'", "")
                 
        return similar_chunks
    
    
    def get_chat_history():
    #Get the history from the st.session_stage.messages according to the slide window parameter
        
        chat_history = []
    
        start_index = max(0, len(st.session_state.messages) - slide_window)
        for i in range (start_index , len(st.session_state.messages) -1):
             chat_history.append(st.session_state.messages[i])
    
        return chat_history
    
        
    def summarize_question_with_history(chat_history, question):
    # To get the right context, use the LLM to first summarize the previous conversation
    # This will be used to get embeddings and find similar chunks in the docs for context
    
        prompt = f"""
            Based on the chat history below and the question, generate a query that extend the question
            with the chat history provided. The query should be in natual language. 
            Answer with only the query. Do not add any explanation.
            
            <chat_history>
            {chat_history}
            </chat_history>
            <question>
            {question}
            </question>
            """
        
        cmd = """
                select snowflake.cortex.complete(?, ?) as response
              """
        df_response = session.sql(cmd, params=[st.session_state.model_name, prompt]).collect()
        sumary = df_response[0].RESPONSE     
    
        sumary = sumary.replace("'", "")
    
        return sumary

    def create_prompt (myquestion):
    
        if st.session_state.use_chat_history:
            chat_history = get_chat_history()
    
            if chat_history != "": #There is chat_history, so not first question
                question_summary = summarize_question_with_history(chat_history, myquestion)
                prompt_context =  get_similar_chunks(question_summary)
            else:
                prompt_context = get_similar_chunks(myquestion) #First question when using history
        else:
            prompt_context = get_similar_chunks(myquestion)
            chat_history = ""
      
        prompt = f"""
               You are an expert chat assistance that extract information from the CONTEXT provided
               between <context> and </context> tags.
               You offer a chat experience considering the information included in the CHAT HISTORY
               provided between <chat_history> and </chat_history> tags..
               When ansering the question contained between <question> and </question> tags
               be concise and do not hallucinate. 
               Only provide answers from the provided context.
               If there is no relevant context provided just say "this information not found"
               If you don´t have the information just say so.
               
               Do not mention the CONTEXT used in your answer.
               Do not mention the CHAT HISTORY used in your asnwer.
               
               <chat_history>
               {chat_history}
               </chat_history>
               <context>          
               {prompt_context}
               </context>
               <question>  
               {myquestion}
               </question>
               Answer: 
               """
    
        return prompt

   
    
    def complete(myquestion):
    
        prompt =create_prompt (myquestion)
        cmd = """
                select snowflake.cortex.complete(?, ?) as response
              """
        
        df_response = session.sql(cmd, params=[st.session_state.model_name, prompt]).collect()
        return df_response
    
    # ### Functions
    
    def main():
            
            st.header('Call Transcript Chatbot:')
            st.write("Above is the list of all the Call transcript for the selected customer:")
        
            config_options()
            init_messages()
             
            # Display chat messages from history on app rerun
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            # Accept user input
            if question := st.chat_input("What do you want to know about the customer call transcripts?"):
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": question})
                # Display user message in chat message container
                with st.chat_message("user"):
                    st.markdown(question)
                # Display assistant response in chat message container
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
            
                    question = question.replace("'","")
            
                    with st.spinner(f"{st.session_state.model_name} thinking..."):
                        response = complete(question)
                        res_text = response[0].RESPONSE     
                    
                        res_text = res_text.replace("'", "")
                        message_placeholder.markdown(res_text)
                
                st.session_state.messages.append({"role": "assistant", "content": res_text})
    
    
    if __name__ == "__main__":
        main()



with tab2:
#List of unique customer_ids 
        
    #To set color to the resolution column in calls table
    def color_resoulution(val):
        color = 'green' if val=='resolved' else 'yellow'
        return f'background-color: {color}'

    st.header("Customer Call Analytics Dashboard")

    
    # filter down to the selected customer only on calls and customer data
    customer_survey = session.table('sandbox.meghana.CALL_TRANSCRIPTS').filter(F.col('customer')==st.session_state.customer_name).to_pandas()
    # customer_calls = session.table('SANDBOX.MEGHANA.SYNTHETIC_CALL_NOTES').filter(F.col('CUSTOMER_ID')==st.session_state.customer_name).to_pandas()
    
    # # st.dataframe(customer)
    # #creating a sub table with important attributes based off of the customer data 
    customer_df = pd.DataFrame(customer_survey)

    call_df = pd.DataFrame(customer_survey)
    call_df_show = call_df.drop([ 'TRANSCRIPT', 'TRANSLATION_MIXTRAL_COMPLETE',
                                 'VEC'],axis=1)

    st.write(":blue[Customer Call Reasons:]")
    st.write(call_df_show.TOPIC_SUMMARY.unique())
    #st.write(call_df_show)
    col1, col2= st.columns(2)

    with col1:
        st.write(":blue[Average Customer Sentiment:]")
        st.write(call_df_show.loc[:, 'SENTIMENT'].mean())
    with col2:
        st.write(":blue[Total Customer Calls:]")
        st.write(call_df_show.loc[:, 'CUSTOMER'].count())


    st.markdown("""
    <style>
    .big-font {
        font-size:22px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    
    st.markdown('<p class="big-font">Average Sentiment by Call Date</p>', unsafe_allow_html=True)
    # fig, ax = plt.subplots()
    # ax.hist(call_df_show.SENTIMENT)
    # st.pyplot(fig)

    mean_values = call_df_show.groupby('DATE_CREATED')['SENTIMENT'].mean()

    st.line_chart(
    mean_values,
    y="SENTIMENT",
    color=["#FF0000"],  # Optional
)



        

# f.lit to get the value of last 5 summary - in pyspark - how to get a value 
