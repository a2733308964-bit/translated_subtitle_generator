def process_file(input_path, output_path, processing_steps):
    """
    每个步骤为 (处理函数, 参数字典) 的元组，例如：
    - (func, {'arg1': val}) → 带参数
    - (func, {})             → 无额外参数
    - (func, None)           → 也支持直接传 None 表示无参数
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for func, params in processing_steps:
        if params:  # 有参数就解包传入
            lines = func(lines, **params)
        else:       # 否则只传 lines
            lines = func(lines)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print(f"✅ 已处理并保存：{output_path}")

