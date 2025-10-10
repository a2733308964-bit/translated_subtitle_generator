"""
batch_whisper_to_txt.py

批量将编号 46–60 的视频/音频文件转写为纯文本 TXT 文件。
依赖: pip install -U openai-whisper tqdm
"""

import re
from pathlib import Path
from tqdm import tqdm
import whisper

# ------- 配置 -------
VIDEO_DIR = Path("/Users/a2733/Downloads/movies")  # 视频文件夹
START_NUM = 46
END_NUM = 60
EXTENSION = ".mp4"         # 文件扩展名
MODEL = "medium"            # 模型: tiny, base, small, medium, large
OUTPUT_DIR = VIDEO_DIR / "txt_output"
CLEAN_TEXT = True
# --------------------

def clean_text(text: str) -> str:
    r"""简单清理文本，去掉 \N、[] () 内内容，多余空格"""
    if not text:
        return ""
    text = text.replace("\\N", " ").replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\(.*?\)", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading whisper model '{MODEL}' ...")
    model = whisper.load_model(MODEL)

    for i in range(START_NUM, END_NUM + 1):
        filepath = VIDEO_DIR / f"{i}{EXTENSION}"
        if not filepath.exists():
            print(f"[跳过] 文件不存在: {filepath}")
            continue

        print(f"\nTranscribing {filepath.name} ...")
        result = model.transcribe(str(filepath))
        segments = result.get("segments", [])

        if not segments:
            print(f"[警告] {filepath.name} 没有转写结果")
            continue

        # 合并所有片段的文字
        full_text = " ".join(seg.get("text", "").strip() for seg in segments)
        if CLEAN_TEXT:
            full_text = clean_text(full_text)

        out_txt = OUTPUT_DIR / f"{i}.txt"
        with out_txt.open("w", encoding="utf-8") as f:
            f.write(full_text)

        print(f"[完成] 已生成 {out_txt}")

    print("\n全部完成。")

if __name__ == "__main__":
    main()