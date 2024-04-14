from langchain.agents.openai_assistant import OpenAIAssistantRunnable

import os
import config

from openai_utils import ChatGPT

import logging

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from openai import AsyncOpenAI

# setup openai--=
os.environ["OPENAI_API_KEY"] = config.openai_api_key
openai = AsyncOpenAI(api_key=config.openai_api_key)
# async_openai = AsyncOpenAI(api_key=config.openai_api_key)

logger = logging.getLogger(__name__)

OPENAI_COMPLETION_OPTIONS = {
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}

class AgentChatGPT(ChatGPT):
    def __init__(self, model="open-ai-assistant"):
        assert model in {"text-davinci-003", "gpt-3.5-turbo-16k", "gpt-3.5-turbo", "gpt-4", "gpt-4-1106-preview", "gpt-4-vision-preview", "open-ai-assistant"}, f"Unknown model: {model}"
        self.model = model

    async def send_message(self, message, dialog_messages=[], chat_mode="buffet_assistant"):
        if chat_mode not in config.chat_modes.keys():
            raise ValueError(f"Chat mode {chat_mode} is not supported")

        n_dialog_messages_before = len(dialog_messages)
        answer = None
        logger.debug(f"!!! chat_mode: {chat_mode}")
        while answer is None:
            try:
                if self.model in {"gpt-3.5-turbo-16k", "gpt-3.5-turbo", "gpt-4", "gpt-4-1106-preview", "gpt-4-vision-preview"}:
                    messages = self._generate_prompt_messages(message, dialog_messages, chat_mode)
                    logger.info('!!! MESSAGES: ', messages)
                    r = await openai.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        **OPENAI_COMPLETION_OPTIONS
                    )
                    answer = r.choices[0].message["content"]
                elif self.model == "open-ai-assistant":
                    agent = OpenAIAssistantRunnable(assistant_id=config.chat_modes[chat_mode]["assistant_id"], as_agent=True)
                    r = agent.invoke({"content": message})
                    answer = r.return_values["output"]
                else:
                    raise ValueError(f"Unknown model: {self.model}")

                answer = self._postprocess_answer(answer)
                n_input_tokens, n_output_tokens = 0, 0
            except Exception as e:  # too many tokens
                raise e
                # if len(dialog_messages) == 0:
                    # raise ValueError("Dialog messages is reduced to zero, but still has too many tokens to make completion") from e

                # forget first message in dialog_messages
                dialog_messages = dialog_messages[1:]

        n_first_dialog_messages_removed = n_dialog_messages_before - len(dialog_messages)

        return answer, (n_input_tokens, n_output_tokens), n_first_dialog_messages_removed


