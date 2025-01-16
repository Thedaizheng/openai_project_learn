import json

from fastapi import FastAPI
import random
import uvicorn
import gradio as gr
import openai
import os
from first_chatbot import chatbot_ui
import utils


class Chatbot:
    def __init__(self):
        self.name = "戴政的小助理机器人"
        self.gpt_model = "gpt-3.5-turbo-1106"
        self.client = openai.OpenAI(api_key=os.getenv("api_key"))

    def generate_ui(self):
        chatbotUI = chatbot_ui.ChatbotUI(self)
        return chatbotUI.generate_ui()

    def _system_role(self, system_prompt="戴政的小助理机器人"):
        return f'''
# role: 你是{system_prompt}
## rule
- 并且具备<role>的工作能力
- 用户询问身份需要表明{system_prompt}
## init
作为<role>，请严格遵守<rule>
        '''

    # 首先这一函数将 Gradio文本框中的数据拿到将其转化为GPT交互的上下文格式
    # 将上下文格式传入_chat_normal进行处理
    def handle_msg(self, user_msg, history, request: gr.Request, system_prompt, temperature):
        # 构建GPT上下文
        if system_prompt == "":
            messages = utils.gradio_history_to_openai_messages(history, system_role=self._system_role())
        else:
            messages = utils.gradio_history_to_openai_messages(history, system_role=self._system_role(system_prompt))

        # 认为这是一条普通的上下文 当作文本进行处理
        for rs in self._chat_normal(user_msg, messages, request, temperature):
            yield rs

    # 用于处理相关的对话信息
    # 首先将当前用户问题添加到上下文信息当中
    # 通过client.chat.completions与GPT进行交互
    # 判断有没有命中插件 命中插件则按照插件处理 未命中则直接处理
    def _chat_normal(self, user_msg, messages, request, temperature):
        messages.append({
            "role": "user",
            "content": user_msg
        })

        # 请求GPT
        chat_completion_chunks = self.client.chat.completions.create(
            messages=messages,
            model=self.gpt_model,
            stream=True,
            temperature=temperature
        )
        for rs in self._handle_normal_msg(chat_completion_chunks):
            yield rs

    # 上一个函数_chat_normal已经得到了与GPT的交互结果这里根据结果进行流式输出返回相关的信息
    def _handle_normal_msg(self, chat_completion_chunks):
        for one in chat_completion_chunks:
            msg = one.choices[0].delta.content
            if msg is not None:
                yield msg
