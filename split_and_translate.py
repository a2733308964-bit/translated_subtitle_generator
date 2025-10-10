import re
import requests

def split_and_translate(
        text,
        api_key,
        api_url="https://api.deepseek.com/v1/chat/completions",
        system_prompt_template=None,
        chunk_size=2000  # 单词数
):
    """
    长文本翻译，按单词数分块并回退到最近标点保证完整句子。

    参数:
        text: 待翻译文本
        api_key: DeepSeek API Key
        api_url: API 地址
        system_prompt_template: 系统提示模板
        chunk_size: 每次翻译最大单词数
    返回:
        翻译后的完整文本
    """
    if system_prompt_template is None:
        system_prompt_template = """
        你是字幕断句和翻译助手。输入英文字幕：
        {subtitle_text}
        输出规则：
        每句先输出英文，再输出中文翻译
        """

    # 正则匹配句子结尾
    sentence_end_re = re.compile(r'[.!?]')
    result_text = ""

    words = text.split()
    start_idx = 0
    total_words = len(words)

    while start_idx < total_words:
        # 按单词数截取块
        end_idx = min(start_idx + chunk_size, total_words)
        chunk_words = words[start_idx:end_idx]
        current_chunk = " ".join(chunk_words)

        # 回退到最近标点
        matches = list(sentence_end_re.finditer(current_chunk))
        if matches:
            last_punct = matches[-1].end()
            # 按字符切分再按单词数对应
            current_chunk = current_chunk[:last_punct].strip()
            # 更新 end_idx 对应新的单词数
            end_idx = start_idx + len(current_chunk.split())

        if not current_chunk:
            start_idx = end_idx
            continue

        # 构建 Prompt
        system_prompt = system_prompt_template.format(subtitle_text=current_chunk)

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": current_chunk}
            ],
            "temperature": 0.2
        }
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.post(api_url, json=payload, headers=headers)
        translated_chunk = response.json()["choices"][0]["message"]["content"]

        # 拼接结果
        if start_idx == 0:
            result_text += translated_chunk
        else:
            result_text += "\n" + translated_chunk

        # 更新起始位置
        start_idx = end_idx

    return result_text