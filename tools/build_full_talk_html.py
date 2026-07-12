from pathlib import Path
import html
import re

ROOT = Path(r"D:\zhc\youth-faith-course-prep")
SRC = ROOT / "01_faith_science_rationality" / "53_revised_real_experience_talk_script.md"
OUT = ROOT / "docs" / "full-talk-script.html"


def inline(text: str) -> str:
    text = html.escape(text.strip())
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text


def slug(index: int) -> str:
    return f"sec-{index:02d}"


def flush_paragraph(parts, output):
    if parts:
        output.append(f"<p>{inline(' '.join(parts))}</p>")
        parts.clear()


def render_markdown(markdown: str):
    lines = markdown.splitlines()
    title = "完整讲稿"
    output = []
    nav = []
    paragraph = []
    in_list = False
    in_table = False
    skip_public_note = False
    section_index = 0
    section_open = False

    def close_list():
        nonlocal in_list
        if in_list:
            output.append("</ul>")
            in_list = False

    def close_table():
        nonlocal in_table
        if in_table:
            output.append("</tbody></table>")
            in_table = False

    for raw in lines:
        line = raw.rstrip()

        if line.startswith("# "):
            title = line[2:].strip()
            continue

        if line.startswith("> 使用说明"):
            skip_public_note = True
            continue
        if skip_public_note:
            if not line:
                skip_public_note = False
            continue

        if not line:
            flush_paragraph(paragraph, output)
            close_list()
            close_table()
            continue

        if line.startswith("|") and line.endswith("|"):
            flush_paragraph(paragraph, output)
            close_list()
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if all(set(cell) <= {"-", ":"} for cell in cells):
                continue
            if not in_table:
                output.append('<table class="ref-table"><tbody>')
                in_table = True
            tag = "th" if cells and cells[0] == "主题" else "td"
            output.append("<tr>" + "".join(f"<{tag}>{inline(cell)}</{tag}>" for cell in cells) + "</tr>")
            continue
        else:
            close_table()

        if line.startswith("## "):
            flush_paragraph(paragraph, output)
            close_list()
            close_table()
            if section_open:
                output.append("</section>")
            section_index += 1
            text = line[3:].strip()
            sid = slug(section_index)
            nav.append((sid, text))
            output.append(f'<section id="{sid}"><h2>{inline(text)}</h2>')
            section_open = True
            continue

        if line.startswith("### "):
            flush_paragraph(paragraph, output)
            close_list()
            output.append(f"<h3>{inline(line[4:])}</h3>")
            continue

        if line.startswith("- "):
            flush_paragraph(paragraph, output)
            if not in_list:
                output.append("<ul>")
                in_list = True
            output.append(f"<li>{inline(line[2:])}</li>")
            continue

        if line.startswith("> "):
            flush_paragraph(paragraph, output)
            close_list()
            output.append(f'<blockquote>{inline(line[2:])}</blockquote>')
            continue

        paragraph.append(line)

    flush_paragraph(paragraph, output)
    close_list()
    close_table()
    if section_open:
        output.append("</section>")
    return title, nav, "\n".join(output)


def main():
    title, nav, body = render_markdown(SRC.read_text(encoding="utf-8"))
    nav_html = "\n".join(f'<a href="#{sid}">{inline(text)}</a>' for sid, text in nav)
    doc = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{inline(title)}</title>
  <style>
    :root {{
      --ink: #171717;
      --muted: #59636c;
      --paper: #faf8f2;
      --panel: #ffffff;
      --line: #d9ded8;
      --green: #1f6b4a;
      --blue: #315f7d;
      --gold: #9a6a1d;
      --soft-green: #e6f2ea;
      --soft-blue: #e8f0f5;
      --shadow: 0 18px 45px rgba(18, 25, 31, .12);
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: #e7ece8;
      font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", Arial, sans-serif;
      line-height: 1.72;
    }}
    a {{ color: inherit; }}
    .page {{
      width: min(1240px, calc(100% - 40px));
      margin: 24px auto;
      background: var(--paper);
      border: 1px solid var(--line);
      box-shadow: var(--shadow);
    }}
    header {{
      padding: 38px 42px 32px;
      background: linear-gradient(120deg, rgba(31, 107, 74, .09), rgba(49, 95, 125, .08)), var(--panel);
      border-bottom: 4px solid var(--ink);
    }}
    .eyebrow {{ margin: 0 0 10px; color: var(--green); font-size: 14px; font-weight: 900; }}
    h1 {{ margin: 0; max-width: 980px; font-size: clamp(30px, 4vw, 48px); line-height: 1.14; letter-spacing: 0; }}
    .subtitle {{ max-width: 900px; margin: 14px 0 0; color: var(--muted); font-size: 18px; font-weight: 700; }}
    .top-actions {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 22px; }}
    .top-actions a {{ display: inline-block; padding: 9px 12px; border: 1px solid var(--line); background: var(--panel); text-decoration: none; font-weight: 900; border-radius: 6px; }}
    .core-line {{
      margin-top: 22px;
      padding: 18px 20px;
      background: var(--ink);
      color: white;
      font-size: 23px;
      font-weight: 900;
      line-height: 1.36;
    }}
    .layout {{ display: grid; grid-template-columns: 260px minmax(0, 1fr); }}
    nav {{ position: sticky; top: 0; height: 100vh; overflow: auto; padding: 22px 18px; background: #f4f6f1; border-right: 1px solid var(--line); }}
    nav h2 {{ margin: 0 0 14px; font-size: 16px; }}
    nav a {{ display: block; margin: 0 0 8px; padding: 9px 10px; background: var(--panel); border: 1px solid var(--line); text-decoration: none; font-size: 14px; font-weight: 800; border-radius: 6px; }}
    nav a:hover {{ border-color: var(--green); background: var(--soft-green); }}
    main {{ padding: 30px 40px 52px; }}
    section {{ margin: 0 0 34px; scroll-margin-top: 24px; }}
    h2 {{ margin: 0 0 16px; padding-bottom: 10px; border-bottom: 3px solid var(--ink); font-size: 28px; line-height: 1.25; letter-spacing: 0; }}
    h3 {{ margin: 24px 0 10px; font-size: 22px; line-height: 1.3; letter-spacing: 0; color: var(--green); }}
    p {{ margin: 0 0 13px; font-size: 18px; }}
    strong {{ font-weight: 900; }}
    ul {{ margin: 8px 0 16px 22px; padding: 0; font-size: 18px; }}
    li {{ margin: 5px 0; }}
    blockquote {{
      margin: 16px 0;
      padding: 16px 18px;
      background: var(--soft-blue);
      border-left: 8px solid var(--blue);
      font-size: 18px;
      font-weight: 800;
    }}
    .ref-table {{ width: 100%; border-collapse: collapse; margin-top: 12px; background: var(--panel); }}
    .ref-table th, .ref-table td {{ border: 1px solid var(--line); padding: 10px 12px; text-align: left; vertical-align: top; font-size: 16px; }}
    .ref-table th {{ background: var(--soft-green); font-weight: 900; }}
    footer {{ padding: 22px 42px 34px; background: var(--panel); border-top: 1px solid var(--line); color: var(--muted); }}
    @media print {{
      body {{ background: #fff; }}
      .page {{ width: 100%; margin: 0; border: none; box-shadow: none; }}
      nav, .top-actions {{ display: none; }}
      .layout {{ display: block; }}
    }}
    @media (max-width: 920px) {{
      .page {{ width: 100%; margin: 0; border: none; }}
      .layout {{ grid-template-columns: 1fr; }}
      nav {{ position: static; height: auto; border-right: none; border-bottom: 1px solid var(--line); }}
      nav a {{ display: inline-block; margin-right: 6px; }}
      header, main, footer {{ padding-left: 20px; padding-right: 20px; }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <header>
      <p class="eyebrow">完整讲稿｜正式版</p>
      <h1>{inline(title)}</h1>
      <p class="subtitle">根据 53_revised_real_experience_talk_script.md 生成。以真实经历为主线，讲信仰、学习、迷茫、AI 时代和神一步步的带领。</p>
      <div class="top-actions">
        <a href="./">返回首页</a>
        <a href="real-experience-faith-talk.html">打开 HTML 幻灯片</a>
        <a href="parent-reminder-script-revised.pptx">下载 PPTX</a>
        <a href="https://github.com/cuizihao1992/youth-faith-course-prep/blob/main/01_faith_science_rationality/53_revised_real_experience_talk_script.md">查看 Markdown 源稿</a>
      </div>
      <div class="core-line">遇到困难的时候，不要一个人躲起来，要回到神面前。</div>
    </header>
    <div class="layout">
      <nav>
        <h2>讲稿导航</h2>
        {nav_html}
      </nav>
      <main>
        {body}
      </main>
    </div>
    <footer>这页以 Markdown 正式讲稿为来源生成；如需改内容，优先修改 Markdown 源稿。</footer>
  </div>
</body>
</html>
"""
    OUT.write_text(doc, encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
