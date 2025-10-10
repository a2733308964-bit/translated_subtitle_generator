import re

def remove_punctuation(lines):
    content = ''.join(lines)

    # 替换标点为空格
    cleaned = re.sub(r"[^\w\s]", ' ', content)

    # 拆分成行并去掉空行
    cleaned_lines = [line for line in cleaned.strip().splitlines() if line.strip()]

    # 保留单数行（索引 0,2,4...）
    selected_lines = [line.strip() for i, line in enumerate(cleaned_lines) if i % 2 == 0]

    # 最终返回按行列表
    return [line + '\n' for line in selected_lines]