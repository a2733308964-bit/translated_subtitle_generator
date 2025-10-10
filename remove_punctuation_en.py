import re


def remove_punctuation(lines):
    """
    删除每行的标点，但保留换行和原始断句。

    参数:
        lines: list[str]，每行为一条字幕文本

    返回:
        list[str]，每行去掉标点后的文本（末尾带 '\n'）
    """
    cleaned_lines = []
    for line in lines:
        # 删除标点（保留字母、数字、空格）
        cleaned = re.sub(r"[^\w\s]", "", line)
        if cleaned.strip():  # 非空才保留
            cleaned_lines.append(cleaned + '\n')
    return cleaned_lines