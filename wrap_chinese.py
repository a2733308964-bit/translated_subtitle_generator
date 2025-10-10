import re

def wrap_chinese(lines, max_len=14, **kwargs):
    """
    遍历 SRT 行，对中文句子进行自动断句换行（优先标点，不足强断）
    参数：
        lines (List[str]): 原始 SRT 文件的行列表
        max_len (int): 中文句子的最大长度（超出将换行）
    返回：
        List[str]: 换行处理后的行列表
    """
    new_lines = []
    for line in lines:
        # 只处理中文行，排除编号与时间轴
        if re.search(r'[\u4e00-\u9fff]', line) and \
           not re.match(r'^\d+\s*$', line) and \
           not re.match(r'^\d{2}:\d{2}:\d{2},\d{3} -->', line):

            # 断句逻辑直接写在内部（不再单独封装）
            result = []
            current = ''
            for char in line.strip():
                current += char
                if len(current) >= max_len:
                    match = re.search(r'^(.*?)([，。！？；、])[^，。！？；、]*$', current)
                    if match:
                        result.append(match.group(1) + match.group(2))
                        current = current[len(match.group(0)):]
                    else:
                        result.append(current)
                        current = ''
            if current:
                result.append(current)

            # 每行添加断句后的内容（含 \n）
            new_lines.append('\n'.join([r.strip() for r in result]) + '\n')
        else:
            new_lines.append(line)
    return new_lines