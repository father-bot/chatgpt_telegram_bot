from langchain.agents.openai_assistant import OpenAIAssistantRunnable
# from langchain_openai import ChatOpenAI
import os

from .openai_utils import ChatGPT



import logging

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

agent = OpenAIAssistantRunnable(assistant_id="asst_wt0En1rUOLgpmer0jZhX6pV6", as_agent=True)

class AgentChatGPT(ChatGPT):
    async def send_message_for_agent(self, message, dialog_messages=[], chat_mode="assistant"):
        # Call the send_message method from the parent ChatGPT class
        return await self.send_message(message, dialog_messages, chat_mode)


