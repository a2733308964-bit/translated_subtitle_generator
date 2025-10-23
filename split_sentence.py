import stanza
import os

# 初始化 Stanza 英文模型
nlp = stanza.Pipeline('en', processors='tokenize,pos,lemma,depparse', verbose=False)

# 并列断句优先级（只考虑主句并列）
DEP_PRIORITY = ['cc', 'conj']

# 过滤掉不宜断句的依存类型
FILTER_DEPS = ['advcl', 'acl', 'xcomp', 'compound:prt']

# 关系代词列表，用于判断从句开头
REL_PRONOUNS = {'that', 'which', 'who', 'whom', 'whose', 'where', 'when'}

# 标点集合，用于输出和单词计数
PUNCT_SET = {'.', ',', ';', ':', '?', '!', "'", '"', '(', ')', '[', ']', '{', '}'}

def tokens_to_text(tokens):
    """把 token 列表拼成文本，标点前不加空格"""
    words = []
    for t in tokens:
        if t.text in {'.', ',', ';', ':', '?', '!', "'", '"', ')', ']', '}'}:
            if words:
                words[-1] += t.text
            else:
                words.append(t.text)
        elif t.text in {'(', '[', '{'}:
            words.append(t.text)
        else:
            words.append(t.text)
    return " ".join(words)

def token_count(tokens):
    """计算单词数，忽略标点"""
    return sum(1 for t in tokens if t.text not in PUNCT_SET)

def find_root_ancestor(token, tokens):
    """沿 head 回溯到 root，返回最终祖先 token"""
    current = token
    while current.head != 0:
        current = tokens[current.head - 1]
    return current

def is_clause_start(token, tokens):
    """判断 token 是否是从句开头"""
    if token.id == 1:
        return False  # 避免首词断句
    if token.text.lower() in REL_PRONOUNS:
        head = tokens[token.head - 1]
        if head.deprel in ('acl:relcl', 'acl', 'advcl'):
            return True
    if token.deprel == 'mark':
        return True
    return False

def find_np_end(idx, tokens):
    """如果 idx 在名词短语内部，则返回名词短语末尾索引"""
    t = tokens[idx]
    if t.upos not in ('NOUN', 'PROPN', 'ADJ', 'DET'):
        return idx
    np_indices = [idx]
    for j in range(idx + 1, len(tokens)):
        tj = tokens[j]
        if tj.head - 1 in np_indices or tj.deprel in ('compound', 'amod', 'det', 'nmod', 'case'):
            np_indices.append(j)
        else:
            break
    return np_indices[-1]

def find_split_point(sentence):
    """根据从句开头和主句并列选择断句点，并考虑名词短语末尾"""
    doc = nlp(sentence)
    if not doc.sentences:
        return None, False  # 第二个返回值表示是否为 NP 内部右移

    tokens = doc.sentences[0].words
    print(f"\n[句子] {sentence}")
    print("Index\tID\tWORD\tHEAD\tDEPREL\tUPOS")
    for idx, t in enumerate(tokens):
        print(f"{idx}\t{t.id}\t{t.text}\t{t.head}\t{t.deprel}\t{t.upos}")

    mid = len(tokens) // 2
    candidates = []
    main_root = [t for t in tokens if t.head == 0][0]

    for idx, t in enumerate(tokens):
        if t.deprel in FILTER_DEPS:
            continue
        if is_clause_start(t, tokens):
            candidates.append((0, abs(idx - mid), idx, t.text, t.deprel, False))  # 从句左断
            continue
        if t.deprel in DEP_PRIORITY:
            head_token = tokens[t.head - 1] if t.head > 0 else t
            root_token = find_root_ancestor(head_token, tokens)
            if root_token.id == main_root.id:
                score = 1
                candidates.append((score, abs(idx - mid), idx, t.text, t.deprel, False))  # 并列左断

    if not candidates:
        print("⚠️ 未找到合适断句点，返回整句")
        return None, False

    candidates.sort(key=lambda x: (x[0], x[1], x[2]))
    best = candidates[0]
    best_idx = best[2]
    is_np_split = False

    # ⚡ 仅当候选点在名词短语内部才右移
    if tokens[best_idx].upos in ('NOUN', 'PROPN', 'ADJ', 'DET'):
        np_end_idx = find_np_end(best_idx, tokens)
        if np_end_idx > best_idx:
            best_idx = np_end_idx
            is_np_split = True

    if best_idx <= 0 or best_idx >= len(tokens) - 1:
        print("⚠️ 断句点在首尾，不合法，返回整句")
        return None, False

    print(f"✅ 选择断句点: index={best_idx}, word='{tokens[best_idx].text}', deprel='{tokens[best_idx].deprel}'")
    return best_idx, is_np_split

def split_sentence(sentence, max_len=25):
    """递归断句"""

    sentence = sentence.strip()
    doc = nlp(sentence)
    tokens = doc.sentences[0].words
    if token_count(tokens) <= max_len:
        return [tokens_to_text(tokens)]

    split_idx, is_np_split = find_split_point(sentence)
    if split_idx is None:
        return [tokens_to_text(tokens)]

    # 根据是否为 NP 内部断句决定左右切分
    if is_np_split:
        left_tokens = tokens[:split_idx + 1]
        right_tokens = tokens[split_idx + 1:]
    else:
        left_tokens = tokens[:split_idx]
        right_tokens = tokens[split_idx:]

    if not left_tokens or not right_tokens:
        return [tokens_to_text(tokens)]

    result = []
    for part_tokens in [left_tokens, right_tokens]:
        if token_count(part_tokens) > max_len:
            result.extend(split_sentence(tokens_to_text(part_tokens), max_len))
        else:
            result.append(tokens_to_text(part_tokens))
    return result

def split_lines(input_path, output_path, max_len=20):
    """处理 txt 文件，断句后保存"""
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    all_segments = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        segments = split_sentence(line, max_len)
        all_segments.extend(segments)

    with open(output_path, 'w', encoding='utf-8') as f:
        for seg in all_segments:
            f.write(seg + '\n')

    print(f"✅ 处理完成！已保存至 {os.path.abspath(output_path)}")


# 示例执行
