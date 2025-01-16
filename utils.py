from gradio import Request
import base64


def gradio_history_to_openai_messages(history, system_role=""):
    openai_messages = []
    if system_role != "":
        openai_messages.append({
            "role": "system",
            "content": system_role
        })

    for one in history:
        if one[0] == '' or one[1] == '':
            continue

        openai_messages.append({
            "role": "user",
            "content": one[0],
        })

        openai_messages.append({
            "role": "assistant",
            "content": one[1],
        })

    return openai_messages


def get_gpt_chunk_tool_calls(chunk):
    return chunk.choices[0].delta.tool_calls
