from add_style import add_style
from initial_process import initial_process
from process_file import process_file
from remove_punctuation import remove_punctuation
from srt_generator import srt_generator
from split_and_translate import split_and_translate
from forced_aligner import forced_aligner
from swap_order import swap_order
from shift_time import shift_time
import os


if __name__ == "__main__":

    style1 = r"{\fnSongti SC\fs60\an2\bord0\shad1\b1\pos(960,1000)}"
    style2 = r"{\fnHelvetica Neue\fs40\an2\bord0\shad2\b0\pos(960,1000)}"
    sub_path="Why This Modern House Is the Perfect Escape From Modern Life (House Tour).srt"
    mp3_path="1_Why This Modern House Is the Perfect Escape From Modern Life (House Tour)_(Vocals).mp3"
    API_KEY =""
    url = "https://api.deepseek.com/v1/chat/completions"
    prompt = """
    You are a translation assistant.
    Your job is to translate English into Chinese, and output in the following strict format:

    - Each English line is followed by its Chinese translation.
    - Do not merge multiple sentences.
    - Do not omit the English original.
    - Output only the pairs, without extra explanations or blank lines.
    - Break long English sentences into shorter ones according to semantic groups.
    - Replace Chinese punctuations，for example, ， and 。， with spaces.
    - Translation style should be elegant, and concise.
    - Do not translate names.

    Example:
    Hello.
    你好
    I like music.
    我喜欢音乐
    """


    process_file(sub_path, "en_ch.txt", [(initial_process, {}), (split_and_translate, {"api_key":API_KEY,"api_url":url,"system_prompt_template":prompt,"chunk_size":1000 })])
    process_file("en_ch.txt", "non_punc.txt", [(remove_punctuation, {})])
    process_file("non_punc.txt","align.json",[(forced_aligner, {"audio_path":mp3_path})])
    srt_generator("non_punc.txt","align.json","en_ch.txt","subtitle.srt")
    process_file("subtitle.srt","subtitle.srt",[
                    (swap_order,{}),
                   (add_style, {"style_line1": style1, "style_line2": style2}),
                   (shift_time,{"shift_start": 0, "shift_end": 0})])

    # os.remove("non_punc.txt")
    # os.remove("align.json")
    # os.remove("en_ch.txt")


    # 播放系统自带铃声
    os.system('afplay /System/Library/Sounds/Glass.aiff')