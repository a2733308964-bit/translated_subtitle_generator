from remove_punctuation import *
from initial_process import *
from process_file import *
from translate import *
from forced_aligner import *
from srt_generator import *
from add_style import *
from swap_order import *
from shift_time import *
from split_sentence import *
import os



if __name__ == "__main__":
    # 把process_file做成装饰器
    style1 = r"{\fnSongti SC\fs60\an2\bord0\shad1\b1\pos(960,1000)}"
    style2 = r"{\fnHelvetica Neue\fs40\an2\bord0\shad2\b0\pos(960,1000)}"
    AUDIO_PATH = "1_Why This Modern House Is the Perfect Escape From Modern Life (House Tour)_(Vocals).mp3"
    SRT_PATH = "Why This Modern House Is the Perfect Escape From Modern Life (House Tour).srt"
    API_KEY = "sk-6a54a17e381947b1ad6b3d765c0ee467"
    URL = "https://api.deepseek.com/v1/chat/completions"
    prompt = """
    输入格式：
    {subtitle_text}

    输出要求：
    1. 严格保持原文的断行结构，逐行对应翻译
    2. 每行先输出英文原文，紧接着下一行输出中文翻译
    3. 英文原文必须完全保留，不得省略或修改
    4. 中文翻译要求：
       - 风格优雅简洁，符合书面语规范
       - 所有人名、地名等专有名词保留不译
       - 避免在中文翻译中夹杂英文单词（专有名词除外）
       - 确保翻译准确、流畅
    5. 不要添加任何额外说明、注释或空行

    示例：
    原文第一行
    对应的中文翻译
    原文第二行  
    对应的中文翻译
    """


    process_file(SRT_PATH,
                 "test_file0.txt",
                 [(initial_process, {})])
    split_lines("test_file0.txt", "test_file1.txt")
    process_file("test_file1.txt",
                 "test_file2.txt",
                 [(translate, {"api_key": API_KEY, "api_url": URL, "system_prompt_template": prompt, "chunk_size": 300})
                  ])
    process_file("test_file2.txt", "non_punc.txt", [(remove_punctuation, {})])
    process_file("non_punc.txt", "align.json", [(forced_aligner, {"audio_path": AUDIO_PATH})])
    srt_generator("non_punc.txt", "align.json", "test_file2.txt", "subtitle.srt")
    process_file("subtitle.srt", "non_punc.srt", [(remove_cn_punctuation, {})])
    process_file("non_punc.srt", "non_punc.srt", [
        (swap_order, {}),
        (add_style, {"style_line1": style1, "style_line2": style2}),
        (shift_time, {"shift_start": 0, "shift_end": 0})
    ])

    # os.remove("non_punc.txt")
    # os.remove("align.json")
    # os.remove("en_ch.txt")
    os.system('afplay /System/Library/Sounds/Glass.aiff')


