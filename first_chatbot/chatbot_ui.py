from fastapi import FastAPI
import random
import uvicorn
import gradio as gr
import openai
import os
from first_chatbot import chatbot_ui

css = """
        .gradio-container {
            background-color: #001f3f; /* 深蓝色背景 */
        }
        h1 { 
            color: white !important; /* 标题字体颜色为白色 */
            margin-top: 20px;        /* 增加顶部间距 */
            margin-bottom: 20px;     /* 增加底部间距 */
        }
    """


class ChatbotUI():

    def __init__(self, chatbot):
        self.chatbot = chatbot

    def generate_ui(self):
        with gr.Blocks() as gr_service:
            # 标题
            gr.Markdown(
                f"<h1 style='text-align: center; margin-bottom: 1rem'>{self.chatbot.name}</h1>")

            # 主界面布局
            with gr.Row():
                # 左侧介绍栏
                with gr.Column(scale=1, min_width=250):
                    # 机器人头像（无框）
                    gr.Image(
                        value="first_chatbot/chatbot_img.webp",  # 替换为实际本地路径
                        interactive=False,
                        show_label=False,  # 移除外框
                        height=150
                    )
                    # 文本说明
                    gr.Markdown(
                        """
                        <p>
                        您可以在下方设置机器人的初始功能。<br>
                        </p>
                        """
                    )
                    # API Key 输入框
                    api_key = gr.Textbox(
                        label="输入您的 API Key",
                        placeholder="请输入您的 API Key...",
                        interactive=True,
                        type="password"  # 输入内容以密码形式显示
                    )
                    # 输入框用于设置 system_role
                    system_role = gr.Textbox(
                        label="设置机器人功能",
                        placeholder="请输入初始化系统功能...",
                        interactive=True
                    )
                    # 创造力调节滑动条
                    creativity = gr.Slider(
                        minimum=0.0,
                        maximum=2.0,
                        value=0.7,
                        step=0.1,
                        label="创造力调节",
                        interactive=True
                    )
                    # 商标
                    gr.Image(
                        value="first_chatbot/sdu_img.jpg",  # 替换为实际本地路径
                        interactive=False,
                        show_label=False,  # 移除外框
                        height=150
                    )
                # 右侧聊天界面
                with gr.Column(scale=4):
                    chatbot = gr.Chatbot([], elem_id="chatbot",
                                         height=500,
                                         bubble_full_width=True)
                    with gr.Row():
                        img = gr.UploadButton(
                            "🎨", file_types=["image"], min_width=20)
                        msg = gr.Textbox(
                            scale=4,
                            show_label=False,
                            placeholder="请输入你的问题?...",
                            container=False,
                            interactive=True,
                        )
                    with gr.Row():
                        gr.ClearButton([chatbot, msg], value="清空")

                    # img.upload(
                    #     self._handle_upload_img,
                    #     [chatbot, img], [chatbot, img], queue=True
                    # )

                    msg.submit(
                        self._handle_sub,
                        [msg, chatbot, creativity, system_role], [chatbot, msg, img], queue=True)

        return gr_service.queue()

    def _handle_sub(self, user_msg, history, creativity, system_role, request: gr.Request):
        history.append([user_msg, ""])

        # 使用 system_role 和创造力参数
        system_prompt = system_role
        temperature = creativity

        for rs in self.chatbot.handle_msg(user_msg, history, request, system_prompt, temperature):
            history[-1][1] += rs
            # 生成内容过程中，禁用两个按钮
            yield history, gr.Textbox(interactive=False, value=""), gr.UploadButton(interactive=True)

        # 生成完内容，启用两个按钮
        yield history, gr.Textbox(interactive=True), gr.UploadButton(interactive=True)


    # # 处理图片上传
    # def _handle_upload_img(self, history, file):
    #     history = history + [((file.name,), None)]
    #     # 上传完图片后，禁用用button，一次对话暂时限制一张图片?
    #     return history, gr.UploadButton(interactive=False)
    #
    # # 处理提交请求
    # def _handle_sub(self, user_msg, history, request: gr.Request, *arg):
    #     history.append([user_msg, ""])
    #
    #     for rs in self.chatbot.handle_msg(user_msg, history, request):
    #         history[-1][1] = rs
    #         # 生成内容过程中，禁用用两个btn
    #         yield history, gr.Textbox(interactive=False, value=""), gr.UploadButton(interactive=False)
    #
    #     # 生成完内容，则启用两个btn
    #     yield history, gr.Textbox(interactive=True), gr.UploadButton(interactive=True)
