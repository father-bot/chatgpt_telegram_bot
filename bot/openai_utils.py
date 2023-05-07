import config
import json
import openai
import aiohttp
from aiohttp import FormData
import database

db = database.Database()

n_images = config.n_images

OPENAI_COMPLETION_OPTIONS = {
    "max_tokens": 2048,
    "temperature": 1,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}
   
class ChatGPT:
    def __init__(self, model="gpt-3.5-turbo"):
        assert model in config.model["available_model"], f"Unknown model: {model}"
        self.model = model

    async def send_message(self, message, user_id, dialog_messages=[], chat_mode="assistant"):
        api = db.get_user_attribute(user_id, "current_api")
        api_info = config.api["info"].get(api, {})
        openai.api_key = str(api_info.get("key", ""))
        openai.api_base=str(config.api["info"][api].get("url"))
        n_dialog_messages_before = len(dialog_messages)
        answer = None
        while answer is None:
            try:
                if (self.model in config.model["available_model"]):
                    if self.model != "text-davinci-003":
                        messages = self._generate_prompt_messages(message, dialog_messages, chat_mode)
                        OPENAI_COMPLETION_OPTIONS["messages"] = messages
                        OPENAI_COMPLETION_OPTIONS["model"] = self.model
                    else:
                        prompt = self._generate_prompt(message, dialog_messages, chat_mode)
                        OPENAI_COMPLETION_OPTIONS["prompt"] = prompt
                        OPENAI_COMPLETION_OPTIONS["engine"] = self.model
                    r = await openai.ChatCompletion.acreate(
                        stream=True,
                        **OPENAI_COMPLETION_OPTIONS
                    )
                    answer = ""
                    if self.model != "text-davinci-003":
                        async for r_item in r:
                            delta = r_item.choices[0].delta
                            if "content" in delta:
                                answer += delta.content
                                yield "not_finished", answer
                    else:
                        async for r_item in r:
                            answer += r_item.choices[0].text
                            yield "not_finished", answer
                else:
                    raise ValueError(f"Modelo desconocido: {self.model}")
                answer = self._postprocess_answer(answer)
            except openai.error.InvalidRequestError as e:  # too many tokens
                if len(dialog_messages) == 0:
                    raise ValueError("Mensajes de diálogo se reduce a cero, pero todavía tiene demasiados tokens para hacer la finalización") from e
                # forget first message in dialog_messages
                dialog_messages = dialog_messages[1:]
        yield "finished", answer

    def _generate_prompt(self, message, dialog_messages, chat_mode):
        prompt = f'system_message({config.chat_mode["info"][chat_mode]["prompt_start"]})'
        prompt += "\n\n"

        # add chat context
        if len(dialog_messages) > 0:
            #prompt += "Chat:\n"
            for dialog_message in dialog_messages:
                prompt += f"User: {dialog_message['user']}\n"
                prompt += f'{chat_mode}: {dialog_message["bot"]}\n'

        # current message
        prompt += f"User: {message}\n"
        prompt += f'{chat_mode}'

        return prompt

    def _generate_prompt_messages(self, message, dialog_messages, chat_mode):
        prompt = config.chat_mode["info"][chat_mode]["prompt_start"]
        messages = [{"role": "system", "content": f'{chat_mode} {prompt}'}]
        for dialog_message in dialog_messages:
            messages.append({"role": "user", "content": dialog_message["user"]})
            messages.append({"role": "assistant", "content": dialog_message["bot"]})
        messages.append({"role": "user", "content": message})

        return messages
    def _postprocess_answer(self, answer):
        answer = answer.strip()
        return answer

async def transcribe_audio(audio_file):
    r = await openai.Audio.atranscribe("whisper-1", audio_file)
    return r["text"]

async def generate_images(prompt, user_id):
    api = db.get_user_attribute(user_id, "current_api")
    api_info = config.api["info"].get(api, {})
    openai.api_key = str(api_info.get("key", ""))
    openai.api_base=str(config.api["info"][api].get("url"))
    r = await openai.Image.acreate(prompt=prompt, n=n_images, size="1024x1024")
    image_urls = [item.url for item in r.data]
    return image_urls

async def is_content_acceptable(prompt):
    r = await openai.Moderation.acreate(input=prompt)
    return not all(r.results[0].categories.values())
