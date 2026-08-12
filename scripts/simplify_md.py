import os, re, sys

target = r"G:\claude 记忆\大白话版"

for root, dirs, files in os.walk(target):
    for f in files:
        if not f.endswith('.md'):
            continue
        path = os.path.join(root, f)
        with open(path, 'r', encoding='utf-8') as fh:
            content = fh.read()
        # 去掉 YAML frontmatter
        content = re.sub(r'^---\n.*?---\n', '', content, flags=re.DOTALL)
        # 去掉 wikilink 标记
        content = re.sub(r'\[\[([^\]]+)\]\]', r'\1', content)
        # 去掉多余空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(content.strip() + '\n')

print(f"处理完成，共处理 {len([1 for r,d,fs in os.walk(target) for f in fs if f.endswith('.md')])} 个文件")
