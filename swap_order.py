def swap_order(lines):
    """
    检查每个字幕块：
    如果一个序号下面正好有 4 行（时间 + 中文 + 英文 + 空行），
    就交换中英文行（即第2、3行）。
    """
    swapped_lines = []
    block = []

    for line in lines:
        if line.strip().isdigit():
            # 遇到新序号，先处理上一个 block
            if block:
                if len(block) == 5:  # 序号 + 时间 + 字幕1 + 字幕2 + 空行
                    block[2], block[3] = block[3], block[2]
                swapped_lines.extend(block)
                block = []
        block.append(line)

    # 处理最后一个 block
    if block:
        if len(block) == 5:
            block[2], block[3] = block[3], block[2]
        swapped_lines.extend(block)

    return swapped_lines

