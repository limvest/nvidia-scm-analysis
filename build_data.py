#!/usr/bin/env python3
"""
build_data.py: 리포트 md 파싱 -> JS 데이터 생성 -> index.html 빌드
"""
import re, json, os, sys

BASE      = os.environ.get("SCM_SOURCE_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "source"))
CHART_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_MD = os.path.join(BASE, "NVIDIA_Rubin_SCM_최종리포트.md")
FEYNMAN   = {
    "F1": os.path.join(BASE, "F1_OIO_TeraPHY.md"),
    "F2": os.path.join(BASE, "F2_QD_Silicon_Quintessent.md"),
    "F3": os.path.join(BASE, "F3_TSMC_HighNA_EUV.md"),
    "F4": os.path.join(BASE, "F4_HBM5_CXL_Packaging.md"),
    "F5": os.path.join(BASE, "F5_Feynman_Patent_Investment.md"),
}
TEMPLATE  = os.path.join(CHART_DIR, "index_template.html")
OUTPUT    = os.path.join(CHART_DIR, "index.html")

def parse_report(filepath):
    with open(filepath, encoding="utf-8") as f:
        text = f.read()
    sections = {}
    pattern = re.compile(r"^(#{2,4})\s+([\dA-Z]+(?:\.[\dA-Z]+)*)\s+(.+)$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    for i, m in enumerate(matches):
        sec_id = m.group(2)
        title  = m.group(3).strip()
        start  = m.end()
        end    = matches[i+1].start() if i+1 < len(matches) else len(text)
        body   = text[start:end].strip()
        sections[sec_id] = {"title": title, "body": body}
    return sections

def parse_feynman(files):
    result = {}
    for key, path in files.items():
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                content = f.read()
            m = re.search(r"^## (.+)$", content, re.MULTILINE)
            title = m.group(1).strip() if m else key
            result[key] = {"title": title, "body": content}
        else:
            print(f"Warning: {path} not found", file=sys.stderr)
    return result

def build_node_section_map():
    return {
        "tsmc":        {"overview": "2.3.1", "risk": "4.2.1"},
        "tsmc_cowos":  {"overview": "2.3.2"},
        "skhynix":     {"overview": "2.3.3"},
        "samsung_m":   {"overview": "2.3.4"},
        "micron":      {"overview": "2.3.5"},
        "foxconn":     {"overview": "2.3.6"},
        "wistron":     {"overview": "2.3.6"},
        "quanta":      {"overview": "2.3.6"},
        "asml":        {"overview": "2.4.1", "risk": "4.2.2"},
        "ajinomoto":   {"overview": "2.4.2", "risk": "4.2.4"},
        "disco":       {"overview": "2.4.3", "risk": "4.2.3"},
        "advantest":   {"overview": "2.4.4"},
        "hanmi":       {"overview": "2.4.5", "risk": "4.2.5"},
        "carl_zeiss":  {"overview": "2.4.6", "risk": "4.2.2"},
        "trumpf":      {"overview": "2.4.7", "risk": "4.2.2"},
        "hamamatsu":   {"overview": "2.4.8"},
        "resonac":     {"overview": "2.4.9"},
        "shinetsu_si": {"overview": "2.4.10"},
        "sumco":       {"overview": "2.4.10"},
        "coherent":    {"overview": "3A.2.1"},
        "lumentum":    {"overview": "3A.2.2"},
        "marvell":     {"overview": "3A.3.1"},
        "tower":       {"overview": "3A.3.2"},
        "gf":          {"overview": "3A.3.3"},
        "iqe":         {"overview": "3A.3.4"},
        "soitec":      {"overview": "3A.4.2"},
        "aixtron":     {"overview": "3A.4.3"},
        "ayar":        {"overview": "3B.6", "feynman": "F1"},
        "sivers":      {"feynman": "F1"},
        "astera":      {"feynman": "F4"},
        "tsmc_coupe":  {"feynman": "F3"},
        "besi":        {"feynman": "F4"},
        "axt":         {"overview": "3A.4.1"},
        "nvidia":      {"overview": "2.2"},
        "ibiden":      {"overview": "6.2"},
        "arm":         {"overview": "7"},
        "cadence":     {"overview": "7"},
        "synopsys":    {"overview": "7"},
    }

def js_escape(s):
    s = s.replace("\\", "\\\\")
    s = s.replace("`", "\\`")
    s = s.replace("${", "\\${")
    return s

def build_js(sections, node_map):
    lines = ["const REPORT = {"]
    for key, val in sections.items():
        title = js_escape(val["title"])
        body  = js_escape(val["body"])
        lines.append(f'  {json.dumps(key)}: {{title:`{title}`,body:`{body}`}},')
    lines.append("};")
    lines.append("")
    lines.append("const NODE_SECTION_MAP = " +
        json.dumps(node_map, ensure_ascii=False, indent=2) + ";")
    return "\n".join(lines)

def main():
    print("Parsing report...")
    sections = parse_report(REPORT_MD)
    print(f"  Sections: {len(sections)}")

    print("Parsing Feynman files...")
    feynman = parse_feynman(FEYNMAN)
    sections.update(feynman)
    print(f"  Total: {len(sections)}")

    node_map = build_node_section_map()
    js_data  = build_js(sections, node_map)

    with open(TEMPLATE, encoding="utf-8") as f:
        template = f.read()

    if "// %%REPORT_DATA%%" not in template:
        print("ERROR: placeholder not found in template", file=sys.stderr)
        sys.exit(1)

    output = template.replace("// %%REPORT_DATA%%", js_data)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(output)

    size_kb = os.path.getsize(OUTPUT) / 1024
    print(f"Written: {OUTPUT} ({size_kb:.0f} KB)")

if __name__ == "__main__":
    main()
