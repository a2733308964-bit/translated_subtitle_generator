import re
import requests


def translate(
        text,
        api_key,
        api_url="https://api.deepseek.com/v1/chat/completions",
        system_prompt_template=None,
        chunk_size=500  # 单词数
):
    """
    长文本翻译，按单词数分块并回退到最近标点保证完整句子。

    参数:
        text: 待翻译文本（字符串列表，每行一个元素）
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

    # 预处理：清理空行但保留分行结构
    cleaned_lines = [line.strip() for line in text if line.strip()]

    # 新的分块逻辑：按行累加，保持原有分行
    chunks = []
    current_chunk_lines = []
    current_word_count = 0

    for line in cleaned_lines:
        line_word_count = len(line.split())

        # 如果当前行能放入当前块
        if current_word_count + line_word_count <= chunk_size:
            current_chunk_lines.append(line)
            current_word_count += line_word_count
        else:
            # 当前行不能放入，先保存当前块
            if current_chunk_lines:
                chunks.append("\n".join(current_chunk_lines))

            # 如果单行就超过chunk_size，需要按句子分割
            if line_word_count > chunk_size:
                # 对长行按句子分割
                sentences = re.split(r'(?<=[.!?])\s+', line)
                for sentence in sentences:
                    sentence_words = sentence.split()
                    if len(sentence_words) <= chunk_size:
                        chunks.append(sentence)
                    else:
                        # 如果单句还是太长，使用原有的单词分割逻辑
                        words = sentence.split()
                        sub_start = 0
                        while sub_start < len(words):
                            sub_end = min(sub_start + chunk_size, len(words))
                            sub_chunk_words = words[sub_start:sub_end]
                            sub_current_chunk = " ".join(sub_chunk_words)

                            # 回退到最近标点
                            matches = list(sentence_end_re.finditer(sub_current_chunk))
                            if matches:
                                last_punct = matches[-1].end()
                                sub_current_chunk = sub_current_chunk[:last_punct].strip()

                            if sub_current_chunk:
                                chunks.append(sub_current_chunk)

                            sub_start += len(sub_current_chunk.split()) if sub_current_chunk else sub_end - sub_start

                # 重置为新的空块
                current_chunk_lines = []
                current_word_count = 0
            else:
                # 新块从当前行开始
                current_chunk_lines = [line]
                current_word_count = line_word_count

    # 添加最后一个块
    if current_chunk_lines:
        chunks.append("\n".join(current_chunk_lines))

    # 处理每个块
    for i, current_chunk in enumerate(chunks):
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

        try:
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            translated_chunk = response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"API调用出错: {e}")
            translated_chunk = f"[翻译失败: {e}]"

        # 拼接结果
        if i == 0:
            result_text += translated_chunk
        else:
            result_text += "\n" + translated_chunk

    return result_text

