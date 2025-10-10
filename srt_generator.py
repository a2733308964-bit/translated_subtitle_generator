import json
import re

def clean_text(text):
    """删除标点并转换为小写"""
    text = re.sub(r"[^\w\s]", "", text)
    return text.lower().strip()

def seconds_to_time_format(seconds):
    """将秒转换为 HH:MM:SS,MMM 格式"""
    try:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds_only = seconds % 60
        milliseconds = int((seconds % 1) * 1000)
        return f"{hours:02}:{minutes:02}:{int(seconds_only):02},{milliseconds:03}"
    except Exception:
        return "00:00:00,000"

def srt_generator(sentence_txt, gentle_json, eng_chi_file, output_file, line=2, idx=1):
    # 读取文本句子
    with open(sentence_txt, 'r', encoding='utf-8') as f:
        sentences = [s.strip() for s in f.readlines() if s.strip()]

    # 读取对齐 JSON
    with open(gentle_json, 'r', encoding='utf-8') as f:
        gentle_data = json.load(f)

    # 读取中英文句子
    with open(eng_chi_file, 'r', encoding='utf-8') as f:
        eng_chi_sentences = [s.strip() for s in f.readlines()]

    srt_content = ""
    a = 0  # 中英文句子索引
    word_pointer = 0  # JSON 当前处理位置

    for sentence in sentences:
        sentence_words = sentence.split()
        num_words = len(sentence_words)
        if num_words == 0:
            continue

        # 遍历 JSON 找到对应数量的有效单词（跳过 <unk>）
        matched_words = []
        json_idx = word_pointer
        while len(matched_words) < num_words and json_idx < len(gentle_data["words"]):
            w = gentle_data["words"][json_idx]
            if w.get("word") != "<unk>":
                clean_w = clean_text(w.get("word", ""))
                if clean_w:  # 非空
                    matched_words.append((json_idx, w))
            json_idx += 1

        # 没有足够单词就跳过句子，同时指针跳到当前匹配的最后单词 +1
        if len(matched_words) < num_words:
            if matched_words:
                word_pointer = matched_words[-1][0] + 1
            else:
                word_pointer = json_idx
            print(f"[WARN] 跳过句子（对齐单词不足）: {sentence}")
            continue

        # 找首尾时间
        start_time = None
        end_time = None
        start_word_json = ""
        end_word_json = ""
        start_word_sentence = sentence_words[0] if sentence_words else ""
        end_word_sentence = sentence_words[-1] if sentence_words else ""

        for i in range(num_words):
            w = matched_words[i][1]
            if w.get("case") == "success" and "start" in w:
                start_time = seconds_to_time_format(w["start"])
                start_word_json = w.get("word", "")
                break

        for i in reversed(range(num_words)):
            w = matched_words[i][1]
            if w.get("case") == "success" and "end" in w:
                end_time = seconds_to_time_format(w["end"])
                end_word_json = w.get("word", "")
                break



        # 如果首尾未对齐，跳过句子，同时指针跳到最后匹配单词 +1
        if start_time is None or end_time is None:
            # 使用占位时间
            start_time = "00:00:00,000"
            end_time = "00:00:00,001"
            print(f"[WARN] 句子未对齐，使用占位时间: {sentence}")

        # 成功对齐，更新指针
        word_pointer = matched_words[-1][0] + 1

        # 写入 SRT
        srt_content += f"{idx}\n"
        srt_content += f"{start_time} --> {end_time}\n"
        idx += 1

        # 写入中英文句子，跳过空行，每个字幕最多两行
        if line==1:
            # 每条字幕对应 TXT 的一行
            if a < len(eng_chi_sentences):
                line_text = eng_chi_sentences[a].strip()
                a += 1
                if line_text:
                    srt_content += line_text + "\n"
            # 每个字幕块后空行
            srt_content += "\n"
        elif line==2:
            lines_added = 0
            while a < len(eng_chi_sentences) and lines_added < 2:
                line_text = eng_chi_sentences[a].strip()
                a += 1
                if not line_text:
                    continue
                srt_content += line_text + "\n"
                lines_added += 1

        # 每个字幕块后强制空行
        srt_content += "\n"

    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(srt_content)

    print("[INFO] SRT 文件生成完成")