def add_style(lines, style_line1, style_line2):
    """
    给每个 5 行字幕块的 line1 和 line2 添加不同的字体样式信息。
    适用于严格 5 行格式的 SRT 文件：
    序号
    时间
    line1
    line2
    空行

    参数：
        lines (List[str]): 原始 SRT 文件的行列表
        style_line1 (str): line1 的字体样式
        style_line2 (str): line2 的字体样式

    返回：
        List[str]: 添加样式后的行列表
    """
    output_lines = []
    total_lines = len(lines)
    i = 0

    while i < total_lines:
        if i + 4 < total_lines:
            block = lines[i:i+5]
            # 给 line1 和 line2 添加不同字体信息
            block[2] = style_line1 + block[2]
            block[3] = style_line2 + block[3]
            output_lines.extend(block)
            i += 5
        else:
            # 不足 5 行的直接原样加入
            output_lines.append(lines[i])
            i += 1

    return output_lines

