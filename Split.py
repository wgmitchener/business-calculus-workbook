from pathlib import Path
import re
import subprocess

TOC_RE = re.compile(r'\\contentsline\s*{section}{\\numberline\s*{(?P<num>\d+)}(?P<title>[^}]*)}{(?P<page>\d+)}.*')


def parse_toc_line(s):
    if m := TOC_RE.match(s):
        return m.groupdict()
    else:
        return None


def parse_toc_file(path: Path):
    with open(path, 'rt') as h:
        for line in h.readlines():
            if m := parse_toc_line(line):
                yield m

def add_page_ranges(tocs):
    this = next(tocs)
    for ahead in tocs:
        new_this = this | {'begin_page': int(this['page']), 'end_page': int(ahead['page'])}
        new_this['num'] = int(new_this['num'])
        yield new_this
        this = ahead
    new_this = this | {'begin_page': int(this['page']), 'end_page': False}
    new_this['num'] = int(new_this['num'])
    yield new_this


def split_on_toc(split_dir: Path, stem: Path):
    toc_path = stem.with_suffix(".toc")
    pdf_path = stem.with_suffix(".pdf")
    for item in add_page_ranges(parse_toc_file(toc_path)):
        num = item['num']
        title = item['title']
        begin_page = item['begin_page']
        end_page = item['end_page']
        if end_page:
            end_page = end_page - 1
        else:
            end_page = ''
        out_path = split_dir / f"{num:02d} {title}.pdf"
        result = subprocess.check_output(
            ('pdfjam', '-o', out_path,
             '--',
             pdf_path, f"{begin_page}-{end_page}"))
        print(result)


def main():
    stem = Path("Business-calculus-workbook")
    split_dir = Path("Split")
    split_dir.mkdir(parents=True, exist_ok=True)
    split_on_toc(split_dir, stem)


if __name__ == '__main__':
    main()
