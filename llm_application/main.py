import google.generativeai as genai
from typing import List, Tuple
import streamlit as st
import json
import yaml
from abc import ABC, abstractmethod

# Load configuration from YAML file
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

class AIApplication(ABC):
    def __init__(self, model):
        self.model = model

    @abstractmethod
    def interact(self, *args, **kwargs):
        pass

    @abstractmethod
    def export(self, *args, **kwargs):
        pass

    @abstractmethod
    def reset(self):
        pass

class Summarizer(AIApplication):
    def __init__(self, model):
        super().__init__(model)
        self.prompt = "Please summarize the following article for me"

    def interact(self, article: str, temp: float = 1.0) -> List[Tuple[str, str]]:
        input = f"{self.prompt}\n{article}"
        response = self.model.generate_content(
            input,
            generation_config=genai.types.GenerationConfig(temperature=temp),
            safety_settings=config['safety_settings']
        )
        return [(input, response.text)]

    def export(self, chatbot: List[Tuple[str, str]], article: str) -> None:
        target = {"chatbot": chatbot, "article": article}
        with open("summarize.json", "w") as file:
            json.dump(target, file)

    def reset(self):
        return []

class RolePlay(AIApplication):
    def __init__(self, model):
        super().__init__(model)
        self.character = ""
        self.prompt = ""

    def interact(self, chatbot: List[Tuple[str, str]], user_input: str, temp: float = 1.0) -> List[Tuple[str, str]]:
        try:
            messages = []
            for input_text, response_text in chatbot:
                messages.append({'role': 'user', 'parts': [input_text]})
                messages.append({'role': 'model', 'parts': [response_text]})

            messages.append({'role': 'user', 'parts': [user_input]})

            response = self.model.generate_content(
                messages,
                generation_config=genai.types.GenerationConfig(temperature=temp),
                safety_settings=config['safety_settings']
            )

            chatbot.append((user_input, response.text))

        except Exception as e:
            st.error(f"Error occurred: {e}")
            chatbot.append((user_input, f"Sorry, an error occurred: {e}"))
        return chatbot

    def export(self, chatbot: List[Tuple[str, str]]) -> None:
        target = {"chatbot": chatbot, "description": f"Role Play with {self.character}"}
        with open("role_play.json", "w") as file:
            json.dump(target, file)

    def reset(self):
        return self.interact([], self.prompt)

class CustomizedAI(AIApplication):
    def __init__(self, model):
        super().__init__(model)
        self.task = "I can assist you with various tasks. What would you like help with?"
        self.prompt = "You are a helpful AI assistant. Respond to the user's requests appropriately."

    def interact(self, chatbot: List[Tuple[str, str]], user_input: str, temp: float = 1.0) -> List[Tuple[str, str]]:
        try:
            messages = []
            if not chatbot:
                messages.append({'role': 'user', 'parts': [self.prompt]})
                messages.append({'role': 'model', 'parts': ["Understood. I'm ready to assist you. How can I help you today?"]})

            for input_text, response_text in chatbot:
                messages.append({'role': 'user', 'parts': [input_text]})
                messages.append({'role': 'model', 'parts': [response_text]})

            messages.append({'role': 'user', 'parts': [user_input]})

            response = self.model.generate_content(
                messages,
                generation_config=genai.types.GenerationConfig(temperature=temp),
                safety_settings=config['safety_settings']
            )

            chatbot.append((user_input, response.text))

        except Exception as e:
            st.error(f"Error occurred: {e}")
            chatbot.append((user_input, f"Sorry, an error occurred: {e}"))
        return chatbot

    def export(self, chatbot: List[Tuple[str, str]]) -> None:
        target = {"chatbot": chatbot, "description": "Customized AI Conversation"}
        with open("customized_ai.json", "w") as file:
            json.dump(target, file)

    def reset(self):
        return [(self.prompt, "Understood. I'm ready to assist you. How can I help you today?")]

def main():
    st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

    st.sidebar.markdown("2024 NTU Machine Learning Course")

    genai.configure(api_key=config['api_key'])
    model = genai.GenerativeModel(config['model_name'])

    try:
        model.generate_content("test")
        st.sidebar.success("Gemini API connected successfully!")
    except:
        st.sidebar.error("There seems to be something wrong with your Gemini API. Please check your API key.")

    summarizer = Summarizer(model)
    role_play = RolePlay(model)
    customized_ai = CustomizedAI(model)

    tab_summarize, tab_role_play, tab_customized = st.tabs(["📚 Article Summarizer", "🎭 AI Role Play", "🤖 Customized AI"])

    with tab_summarize:
        st.header("Article Summarizer")
        st.markdown("Fill in any article you like and let the AI summarize it for you!")

        article = st.text_area("📝 Article", height=200)
        temperature = st.slider("🌡️ Temperature (Summarizer)", 
                                min_value=config['temperature']['min'], 
                                max_value=config['temperature']['max'], 
                                value=config['temperature']['default'], 
                                step=config['temperature']['step'], 
                                key="temp_sum")
        st.markdown("Temperature controls the creativity of the output. Higher values result in more creative responses.")

        if st.button("🚀 Generate Summary"):
            if article:
                with st.spinner("Generating summary..."):
                    result = summarizer.interact(article, temperature)
                    st.success("Summary generated!")
                    st.write("Summary:")
                    st.info(result[0][1])
            else:
                st.warning("Please enter an article to summarize.")

        if st.button("🔄 Reset Summary"):
            st.rerun()

        if st.button("💾 Export Summary"):
            if article:
                summarizer.export([(summarizer.prompt, article)], article)
                st.success("Exported successfully!")
            else:
                st.warning("No content to export. Please generate a summary first.")

    with tab_role_play:
        st.header("AI Role Play")
        st.markdown("Interact with an AI character in a role-playing scenario!")

        role_play.character = st.text_input("Character for the chatbot", "FILL IN YOUR CHARACTER")
        role_play.prompt = st.text_area("Prompt for roleplay", "FILL IN YOUR PROMPT")

        if 'chatbot' not in st.session_state:
            st.session_state.chatbot = role_play.reset()

        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chatbot:
                st.text_area("User" if st.session_state.chatbot.index(message) % 2 == 0 else "AI", message[1], height=100, disabled=True)

        user_input = st.text_input("Your message")
        temperature = st.slider("🌡️ Temperature (Role Play)", 
                                min_value=config['temperature']['min'], 
                                max_value=config['temperature']['max'], 
                                value=config['temperature']['default'], 
                                step=config['temperature']['step'], 
                                key="temp_role")

        if st.button("Send"):
            if user_input:
                st.session_state.chatbot = role_play.interact(st.session_state.chatbot, user_input, temperature)
                st.rerun()

        if st.button("Reset Conversation"):
            st.session_state.chatbot = role_play.reset()
            st.rerun()

        if st.button("Export Conversation"):
            role_play.export(st.session_state.chatbot)
            st.success("Conversation exported successfully!")

    with tab_customized:
        st.header("Customized AI")
        st.markdown("Interact with an AI that can help you with various tasks!")

        if 'custom_chatbot' not in st.session_state:
            st.session_state.custom_chatbot = customized_ai.reset()

        chat_container = st.container()
        with chat_container:
            for message in st.session_state.custom_chatbot:
                st.text_area("User" if st.session_state.custom_chatbot.index(message) % 2 == 0 else "AI", message[1],
                             height=100, disabled=True)

        user_input = st.text_input("Your message", key="custom_input")
        temperature = st.slider("🌡️ Temperature (Customized AI)", 
                                min_value=config['temperature']['min'], 
                                max_value=config['temperature']['max'], 
                                value=config['temperature']['default'], 
                                step=config['temperature']['step'], 
                                key="temp_custom")

        if st.button("Send", key="custom_send"):
            if user_input:
                st.session_state.custom_chatbot = customized_ai.interact(st.session_state.custom_chatbot, user_input,
                                                                         temperature)
                st.rerun()

        if st.button("Reset Conversation", key="custom_reset"):
            st.session_state.custom_chatbot = customized_ai.reset()
            st.rerun()

        if st.button("Export Conversation", key="custom_export"):
            customized_ai.export(st.session_state.custom_chatbot)
            st.success("Conversation exported successfully!")

    st.sidebar.markdown("---")
    st.sidebar.markdown("zoanana990 (C) CopyRight 2024")

if __name__ == "__main__":
    main()