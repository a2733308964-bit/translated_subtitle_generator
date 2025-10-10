import gentle

def forced_aligner(lines, audio_path, nthreads=4, disfluency=False, conservative=False, **kwargs):
    """
    Gentle 强制对齐（直接返回 JSON 字符串，兼容 process_file）

    参数:
        lines: list[str] 或 str，字幕文本
        audio_path: 音频文件路径
        nthreads: 使用线程数
        disfluency: 是否允许 disfluency
        conservative: 是否使用保守模式
        kwargs: 其他扩展参数

    返回:
        str，JSON 格式字符串（Gentle 对齐结果）
    """
    # 合并文本
    if isinstance(lines, list):
        transcript_text = "".join(lines)
    else:
        transcript_text = lines

    # 加载资源并创建 aligner
    resources = gentle.Resources()
    aligner = gentle.ForcedAligner(
        resources, transcript_text, nthreads=nthreads,
        disfluency=disfluency, conservative=conservative
    )

    # 对音频进行对齐
    with gentle.resampled(audio_path) as wavfile:
        result = aligner.transcribe(wavfile)

    # 直接返回 JSON 字符串
    return result.to_json()