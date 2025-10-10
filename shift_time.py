import re

def shift_time(lines, shift_start=0.0, shift_end=0.0):
    """
    调整每条字幕的开始和结束时间
    正值往后，负值往前
    """
    time_pattern = re.compile(r"(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})")
    output_lines = []

    for line in lines:
        match = time_pattern.match(line)
        if match:
            h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, match.groups())

            start_ms = (h1*3600 + m1*60 + s1)*1000 + ms1 + int(shift_start*1000)
            end_ms   = (h2*3600 + m2*60 + s2)*1000 + ms2 + int(shift_end*1000)

            start_ms = max(0, start_ms)
            end_ms   = max(0, end_ms)

            h1_new = start_ms // (3600*1000)
            m1_new = (start_ms % (3600*1000)) // (60*1000)
            s1_new = (start_ms % (60*1000)) // 1000
            ms1_new = start_ms % 1000

            h2_new = end_ms // (3600*1000)
            m2_new = (end_ms % (3600*1000)) // (60*1000)
            s2_new = (end_ms % (60*1000)) // 1000
            ms2_new = end_ms % 1000

            new_line = f"{h1_new:02d}:{m1_new:02d}:{s1_new:02d},{ms1_new:03d} --> {h2_new:02d}:{m2_new:02d}:{s2_new:02d},{ms2_new:03d}\n"
            output_lines.append(new_line)
        else:
            output_lines.append(line)

    return output_lines