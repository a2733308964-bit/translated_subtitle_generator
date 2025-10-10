import re

def initial_process(lines):
    """
    处理 srt 行列表：清除说话人标签、括号内容，提取字幕内容并合并成一个纯文本段落
    参数:
        lines (List[str]): 原始 .srt 行列表
    返回:
        str: 合并后的纯文本字符串
    """
    text_lines = []
    block = []

    for line in lines:
        stripped = line.strip()

        if stripped == "":
            if len(block) >= 3:
                content_lines = block[2:]

                for content in content_lines:
                    content = re.sub(r'^[A-Z\s]+:\s*', '', content)
                    content = re.sub(r'\[.*?\]', '', content)
                    content = re.sub(r'\(.*?\)', '', content)
                    if content.strip():
                        text_lines.append(content.strip())
            block = []
        else:
            block.append(stripped)

    # 处理最后一个 block（文件末尾无空行时）
    if len(block) >= 3:
        content_lines = block[2:]
        for content in content_lines:
            content = re.sub(r'^[A-Z\s]+:\s*', '', content)
            content = re.sub(r'\[.*?\]', '', content)
            content = re.sub(r'\(.*?\)', '', content)
            if content.strip():
                text_lines.append(content.strip())

    # 合并成一段文字，并清理多余空格
    merged_text = ' '.join(text_lines)
    merged_text = re.sub(r'\s+', ' ', merged_text).strip()

    # 再次清除可能遗留的括号内容（某些不完整跨句括号）
    merged_text = re.sub(r'\[.*?\]', '', merged_text)
    merged_text = re.sub(r'\(.*?\)', '', merged_text)

    return merged_text