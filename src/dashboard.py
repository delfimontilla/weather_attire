import json
import streamlit as st
from get_weather import WeatherFetcher
from recommender import Recommender

def generate_clothes_recommendation():
    weather_params, currently, hourly = get_weather_information()
    generator = Recommender()
    input_text = generator.fill_in_template(currently["date"].iloc[0], weather_params.get("timezone", "GMT"), 
                                            currently.to_dict(orient="records"), hourly.to_dict(orient="records"))
    reco = generator.generate_clothes_recommendation(input_text)
    return reco

def get_weather_information(text_format = False):
    with open("config/baires_config.json", "r") as file:
        config = json.load(file)
    
    weather_params = config.get("params", {})
    cache_params = config.get("cache", {})

    #create a WeatherFetcher object
    weather_fetcher = WeatherFetcher(
        latitude = weather_params.get("latitude", 0),
        longitude = weather_params.get("longitude", 0),
        current = weather_params.get("current", ["temperature_2m"]),
        hourly = weather_params.get("hourly", ["temperature_2m"]),
        timezone = weather_params.get("timezone", "GMT"),
        forecast_days = weather_params.get("forecast_days", 1),
        forecast_hours = weather_params.get("forecast_hours", 6),
        expire_after = cache_params.get("expire_after", 3600),
        n_retries = cache_params.get("n_retries", 1),
        backoff_factor = cache_params.get("backoff_factor", 0.2)
    )
    currently, hourly = weather_fetcher.get_weather()
    if text_format:
        return f"""The current temperature is {currently['temperature_2m'].iloc[0]}°C, 
        the apparent temperature is {currently['apparent_temperature'].iloc[0]}°C, 
        and the probability of precipitation is {currently['precipitation'].iloc[0]}%."""
    else:
        return weather_params, currently, hourly



# Set Streamlit page configuration
st.set_page_config(page_title='Weather Attire Assistant 🤖', layout='wide')
# Initialize session states
if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []
if "just_sent" not in st.session_state:
    st.session_state["just_sent"] = False
if "temp" not in st.session_state:
    st.session_state["temp"] = ""

def clear_text():
    st.session_state["temp"] = st.session_state["input"]
    st.session_state["input"] = ""


# Define function to get user input
def get_text():
    """
    Get the user input text.

    Returns:
        (str): The text entered by the user
    """
    input_text = st.text_input("You: ", st.session_state["input"], key="input", 
                            placeholder="Your AI attire assistant here!", 
                            on_change=clear_text,    
                            label_visibility='hidden')
    input_text = st.session_state["temp"]
    return input_text


    # Define function to start a new chat
def new_chat():
    """
    Clears session state and starts a new chat.
    """
    save = []
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        save.append("User:" + st.session_state["past"][i])
        save.append("Bot:" + st.session_state["generated"][i])        
    st.session_state["stored_session"].append(save)
    st.session_state["generated"] = []
    st.session_state["past"] = []
    st.session_state["input"] = ""
    st.session_state.entity_memory.store = {}
    st.session_state.entity_memory.buffer.clear()

  

with st.sidebar:
    st.markdown("---")
    st.markdown("# About")
    st.markdown("Test the AI Attire Assistant.")
    st.markdown(
       "According to the date, city, and weather."
            )
    info_option = st.selectbox(label='Info to display', options=['Attire Recommendation', 'Weather'])


    
# Set up the Streamlit app layout
st.title("Weather Attire Assistant 🤖")
st.subheader("Powered by OpenMeteo + Gemma AI via Hugging Face + Streamlit")

hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)


# Add a button to start a new chat
#st.sidebar.button("New Chat", on_click = new_chat, type='primary')

# Get the user input
user_input = get_text()

# Generate the output using the ConversationChain object and the user input, and add the input/output to the session
if user_input and info_option == "Attire Recommendation":
    post_response = "Bot: " + generate_clothes_recommendation() 
    st.session_state["generated"].append(post_response)
    st.session_state["past"].append(user_input)
    st.session_state["just_sent"] = True

elif user_input and info_option == "Weather":
    post_response = "Bot: " + get_weather_information(text_format=True) 
    st.session_state["generated"].append(post_response)
    st.session_state["past"].append(user_input)
    st.session_state["just_sent"] = True

# Allow to download as well
download_str = []
# Display the conversation history using an expander, and allow the user to download it
with st.expander("Conversation", expanded=True):
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        st.info(st.session_state["past"][i],icon="🗣️")
        st.success(st.session_state["generated"][i], icon="🤖")
        download_str.append(str(st.session_state["past"][i]))
        download_str.append(str(st.session_state["generated"][i]))
                            
    # Can throw error - requires fix
    download_str = '\n'.join(download_str)
    
    if download_str:
        st.download_button('Download',download_str)

# Display stored conversation sessions in the sidebar
for i, sublist in enumerate(st.session_state.stored_session):
        with st.sidebar.expander(label= f"Conversation-Session:{i}"):
            st.write(sublist)

# Allow the user to clear all stored conversation sessions
if st.session_state.stored_session:   
    if st.sidebar.checkbox("Clear-all"):
        del st.session_state.stored_session

