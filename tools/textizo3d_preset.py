#!/usr/bin/env python3
"""Textizo3D preset helper (Python 3, standard library only).

Commands:
  build     <spec.json> [<out.setting>] [--frames N] [--compact] [--overwrite]   write a preset node from a JSON spec, then check it
  check     <file.setting>... [--frames N]                                       check presets: inputs, values, timing, layout
  to-spec   <file.setting> [<out.json>]                                          turn a preset (or a node saved from Resolve) into a spec
  looks                                                                          list the ready looks in presets/
  textures                                                                       list the textures Textizo3D carries
  where                                                                          print the folders presets can go to
  next-name [--to resolve|downloads|<folder>] [--variant N]                      the next free short name, like Textizo3D-07A
  install   <file.setting>... --to resolve|downloads|<folder> [--overwrite]

A preset is one Textizo3D node (Fusion's settings text) to paste on the Fusion page.
The rules this tool applies are written out in "Textizo3D AI Guide.md".
"""
import argparse
import difflib
import json
import math
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)
INPUTS_PATH = os.path.join(KIT, "reference", "inputs.json")
LAYOUT_PATH = os.path.join(KIT, "reference", "fusion-layout.setting")
PRESETS = os.path.join(KIT, "presets")
MY_PRESETS = os.path.join(KIT, "my-presets")
TOOL_TYPE = "ofx.com.clipizo.textizo3dfx"
NODE_NAME = "Textizo3D1"
PREFIX = "Textizo3D"
COLOR_PARTS = ("Red", "Green", "Blue")

# The In and Out rows: the spec's name, the inputs' middle part (T3In<key>..., T3Out<key>...).
ROWS = [("opacity", "Opacity"), ("blur", "Blur"), ("position", "Pos"), ("size", "Size"), ("tracking", "Track"),
        ("rotation", "Rot"), ("explosion", "Explode")]
ROW_KEYS = dict(ROWS)
ROW_ALIASES = {"fade": "opacity", "alpha": "opacity", "pos": "position", "move": "position", "scale": "size",
               "track": "tracking", "spacing": "tracking", "rot": "rotation", "turn": "rotation",
               "explode": "explosion", "burst": "explosion"}
AXIS_ROWS = {"position", "rotation"}
ROW_FIELDS = {"on", "by", "order", "start", "end", "stagger", "from", "to", "ease",
              "damping", "variance", "spin", "pre_roll", "reverse"}
# Neutral values: what a letter has while its rows are off.
ROW_NEUTRAL = {"opacity": 1.0, "blur": 0.0, "position": 0.0, "size": 1.0, "tracking": 0.0, "rotation": 0.0,
               "explosion": 0.0}

# Fonts found on both Windows and macOS. Others must be installed on the computer that renders,
# unless Textizo3D carries them (reference/inputs.json, "fonts").
SYSTEM_FONTS = {"arial", "arial black", "impact", "georgia", "times new roman", "verdana", "trebuchet ms",
                "courier new", "tahoma", "comic sans ms"}

# Average width of a capital and of a small letter, in units at Size 1 and Tracking 1 (one unit is the font's
# ascent + descent), measured on Textizo3D's renders of "HAMBURGERS" and "hamburgers" (heaviest style).
FONT_WIDTH = {"arial black": (0.56, 0.45), "arial": (0.63, 0.47), "impact": (0.44, 0.41), "anton": (0.33, 0.32),
              "bebas neue": (0.34, 0.34), "oswald": (0.38, 0.33), "archivo black": (0.72, 0.59),
              "luckiest guy": (0.61, 0.63), "bangers": (0.43, 0.43), "montserrat": (0.63, 0.54),
              "poppins": (0.51, 0.47), "inter": (0.59, 0.51), "roboto": (0.57, 0.46), "rubik": (0.62, 0.54),
              "kanit": (0.45, 0.39), "barlow": (0.52, 0.45), "fredoka": (0.53, 0.45), "nunito": (0.53, 0.42),
              "open sans": (0.51, 0.45), "permanent marker": (0.5, 0.42), "georgia": (0.7, 0.55)}
DEFAULT_WIDTH = (0.6, 0.5)
# Arial's advance widths (1/1000 em) for the letters' widths relative to each other.
ARIAL_WIDTHS = dict(zip(
    " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~",
    [278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278] + [556] * 10 +
    [278, 278, 584, 584, 584, 556, 1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833, 722,
     778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469, 556, 333, 556, 556, 500,
     556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556, 556, 556, 333, 500, 278, 556, 500, 722, 500,
     500, 500, 334, 260, 334, 584]))
AVG_CAPS = sum(ARIAL_WIDTHS[c] for c in "HAMBURGERS") / 10.0
AVG_SMALL = sum(ARIAL_WIDTHS[c] for c in "hamburgers") / 10.0


# --------------------------------------------------------------------------- settings text (Lua tables)

class Table:
    """A Lua table from a settings file; `kind` is the constructor name (Input, ofx.com..., ...)."""

    def __init__(self, kind=None):
        self.kind = kind
        self.fields = {}
        self.items = []
        self.duplicates = []
        self.spans = {}

    def get(self, key, default=None):
        return self.fields.get(key, default)


class Ref:
    def __init__(self, name):
        self.name = name


TOKEN_RE = re.compile(r"""
    (?P<ws>\s+)
  | (?P<comment>--\[(?P<ceq>=*)\[.*?\](?P=ceq)\]|--[^\n]*)
  | (?P<str>"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')
  | (?P<longstr>\[(?P<leq>=*)\[.*?\](?P=leq)\])
  | (?P<num>-?(?:0[xX][0-9a-fA-F]+|(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?))
  | (?P<name>[A-Za-z_][A-Za-z0-9_]*)
  | (?P<sym>[{}\[\]=,;().])
""", re.S | re.X)


def unescape_lua(body):
    simple = {"n": "\n", "t": "\t", "r": "\r", "a": "\a", "b": "\b", "f": "\f", "v": "\v",
              "\\": "\\", '"': '"', "'": "'", "\n": "\n"}
    raw = body.encode("utf-8")
    data = bytearray()
    i = 0
    while i < len(raw):
        c = raw[i:i + 1]
        if c != b"\\":
            data += c
            i += 1
            continue
        nxt = raw[i + 1:i + 2].decode("latin-1")
        if nxt in simple:
            data += simple[nxt].encode("utf-8")
            i += 2
        elif nxt.isdigit():
            m = re.match(rb"\d{1,3}", raw[i + 1:])
            data.append(int(m.group(0)) & 0xFF)
            i += 1 + len(m.group(0))
        elif nxt == "x":
            data.append(int(raw[i + 2:i + 4], 16))
            i += 4
        elif nxt == "z":
            i += 2
            while i < len(raw) and raw[i:i + 1].isspace():
                i += 1
        else:
            data += raw[i + 1:i + 2]
            i += 2
    return data.decode("utf-8", "replace")


def tokenize(text):
    pos, tokens = 0, []
    while pos < len(text):
        m = TOKEN_RE.match(text, pos)
        if not m:
            line = text.count("\n", 0, pos) + 1
            raise ValueError("cannot read the settings text at line %d: %r" % (line, text[pos:pos + 20]))
        start, pos = pos, m.end()
        kind = m.lastgroup
        if kind in ("ws", "comment"):
            continue
        if kind in ("ceq", "leq"):
            kind = "longstr" if m.group("longstr") else "comment"
            if kind == "comment":
                continue
        value = m.group(kind)
        if kind == "str":
            tokens.append(("str", unescape_lua(value[1:-1]), start))
        elif kind == "longstr":
            eq = len(m.group("leq"))
            body = value[2 + eq:-(2 + eq)]
            tokens.append(("str", body[1:] if body.startswith("\n") else body, start))
        elif kind == "num":
            tokens.append(("num", float(int(value, 16)) if "x" in value.lower() else float(value), start))
        else:
            tokens.append((kind, value, start))
    return tokens


class Parser:
    def __init__(self, text):
        self.tokens = tokenize(text)
        self.i = 0

    def peek(self, offset=0):
        j = self.i + offset
        return self.tokens[j][:2] if j < len(self.tokens) else ("eof", None)

    def pos(self):
        return self.tokens[self.i][2] if self.i < len(self.tokens) else -1

    def take(self, kind=None, value=None):
        tok = self.peek()
        if (kind and tok[0] != kind) or (value is not None and tok[1] != value):
            raise ValueError("expected %s but found %r" % (value or kind, tok[1]))
        self.i += 1
        return tok

    def value(self):
        kind, val = self.peek()
        if kind == "sym" and val == "{":
            return self.table(None)
        if kind == "str":
            self.i += 1
            return val
        if kind == "num":
            self.i += 1
            return int(val) if val.is_integer() and abs(val) < 1e15 else val
        if kind == "name":
            self.i += 1
            if val in ("true", "false"):
                return val == "true"
            if val == "nil":
                return None
            name = val
            while self.peek() == ("sym", "."):
                self.i += 1
                name += "." + self.take("name")[1]
            if self.peek() == ("sym", "("):
                self.take("sym", "(")
                self.take("sym", ")")
                name += "()"
            if self.peek() == ("sym", "{"):
                return self.table(name)
            return Ref(name)
        raise ValueError("unexpected %r" % (val,))

    def table(self, kind):
        t = Table(kind)
        self.take("sym", "{")
        while self.peek() != ("sym", "}"):
            kind_, val = self.peek()
            if kind_ == "name" and self.peek(1) == ("sym", "="):
                start = self.pos()
                self.i += 2
                key = val
                if key in t.fields:
                    t.duplicates.append(key)
                t.fields[key] = self.value()
                t.spans[key] = start
            elif kind_ == "sym" and val == "[":
                self.i += 1
                key = self.value()
                self.take("sym", "]")
                self.take("sym", "=")
                t.fields[key] = self.value()
            else:
                t.items.append(self.value())
            if self.peek()[0] == "sym" and self.peek()[1] in (",", ";"):
                self.i += 1
        self.take("sym", "}")
        return t


def read_setting_text(text):
    root = Parser(text).value()
    if not isinstance(root, Table):
        raise ValueError("the text does not start with {")
    return root


def find_tools(root):
    """[(name, Textizo3D table)], {spline name: table}, [(other name, kind)]."""
    tools = root.get("Tools")
    if not isinstance(tools, Table):
        raise ValueError("no Tools = ordered() { ... } block")
    found, splines, others = [], {}, []
    for name, tool in tools.fields.items():
        if not isinstance(tool, Table):
            continue
        if (tool.kind or "").lower() == TOOL_TYPE:
            found.append((name, tool))
        elif tool.kind in ("BezierSpline", "LUTBezier"):
            splines[name] = tool
        else:
            others.append((name, tool.kind))
    return found, splines, others


# --------------------------------------------------------------------------- the control list

def load_reference():
    with open(INPUTS_PATH, "r", encoding="utf-8") as handle:
        ref = json.load(handle)
    ref["by_fusion"] = {}
    for key, entry in ref["inputs"].items():
        if entry.get("kind") == "color":
            for part, fid in zip(COLOR_PARTS, entry["fusion"]):
                ref["by_fusion"][fid] = (key, COLOR_PARTS.index(part))
        else:
            ref["by_fusion"][key] = (key, None)
    return ref


def public_inputs(ref):
    return [(key, entry) for key, entry in ref["inputs"].items() if entry.get("role") == "public"]


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def fmt_num(value):
    if isinstance(value, bool):
        value = int(value)
    if isinstance(value, int):
        return str(value)
    value = float(value)
    if value.is_integer() and abs(value) < 1e15:
        return str(int(value))
    text = repr(value)   # the shortest text that reads back as the same number
    if "e" in text or "E" in text:
        text = ("%.12f" % value).rstrip("0").rstrip(".")
    return "0" if text in ("-0", "") else text


def lua_string(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t") + '"'


def norm_word(text):
    return re.sub(r"[\s_\-]+", "", str(text)).lower()


def option_index(entry, value, where):
    """A choice from its index or its label ("Out Cubic", "out_cubic", "outcubic")."""
    options = entry.get("options") or []
    if isinstance(value, bool):
        raise ValueError("%s: use one of %s" % (where, ", ".join(options)))
    if is_number(value):
        if float(value).is_integer() and 0 <= value < len(options):
            return int(value)
        raise ValueError("%s: %s is not one of 0..%d" % (where, fmt_num(value), len(options) - 1))
    want = norm_word(value)
    for i, label in enumerate(options):
        if norm_word(label) == want:
            return i
    raise ValueError("%s: %r is not one of: %s" % (where, value, ", ".join(options)))


def parse_color(value, where, notes=None):
    """[r, g, b] from 0 to 1, from "#RRGGBB", "#RGB" or a list."""
    if isinstance(value, str):
        text = value.strip().lstrip("#")
        if re.fullmatch(r"[0-9a-fA-F]{3}", text):
            text = "".join(c * 2 for c in text)
        if not re.fullmatch(r"[0-9a-fA-F]{6}", text):
            raise ValueError("%s: write a colour as \"#RRGGBB\" or [r, g, b] from 0 to 1" % where)
        return [round(int(text[i:i + 2], 16) / 255.0, 4) for i in (0, 2, 4)]
    if isinstance(value, (list, tuple)) and len(value) in (3, 4) and all(is_number(v) for v in value):
        rgb = [float(v) for v in value[:3]]
        if any(v > 1 for v in rgb) and all(0 <= v <= 255 and float(v).is_integer() for v in rgb):
            if notes is not None:
                notes.append("%s: %s read as 0-255 and divided by 255" % (where, value))
            rgb = [round(v / 255.0, 4) for v in rgb]
        return rgb
    raise ValueError("%s: write a colour as \"#RRGGBB\" or [r, g, b] from 0 to 1" % where)


def color_hex(rgb):
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(round(c * 255)))) for c in rgb)


def coerce(key, entry, value, where, notes=None):
    """The value of input `key` from a spec value, checked against its kind (raises ValueError)."""
    kind = entry.get("kind")
    if kind == "color":
        return parse_color(value, where, notes)
    if kind == "choice":
        return option_index(entry, value, where)
    if kind == "checkbox":
        if isinstance(value, bool):
            return int(value)
        if value in (0, 1):
            return int(value)
        raise ValueError("%s: use true or false (or 1 or 0)" % where)
    if kind in ("number", "integer"):
        if not is_number(value):
            raise ValueError("%s: needs a number" % where)
        if kind == "integer":
            if not float(value).is_integer():
                raise ValueError("%s: needs a whole number (frames are whole)" % where)
            value = int(value)
        return value
    if kind in ("text", "string", "file"):
        if not isinstance(value, str):
            raise ValueError('%s: needs text in quotes, like "Hello"' % where)
        return value
    raise ValueError("%s: %s is not an input a preset sets" % (where, key))


# --------------------------------------------------------------------------- values <-> settings text

def defaults(ref):
    out = {}
    for key, entry in public_inputs(ref):
        d = entry.get("default")
        out[key] = list(d) if isinstance(d, list) else d
    return out


def same_value(a, b):
    if isinstance(a, list) or isinstance(b, list):
        return isinstance(a, list) and isinstance(b, list) and len(a) == len(b) and all(
            abs(float(x) - float(y)) < 1e-6 for x, y in zip(a, b))
    if is_number(a) and is_number(b):
        return abs(float(a) - float(b)) < 1e-6
    return a == b


def tool_values(tool, ref, report=None):
    """{input key: value} of a Textizo3D node's Inputs (colours gathered as [r, g, b])."""
    inputs = tool.get("Inputs")
    values, partial, animated = {}, {}, []
    if not isinstance(inputs, Table):
        return values, animated
    for fid, inp in inputs.fields.items():
        if not isinstance(inp, Table):
            if report:
                report.error("%s is not written as Input { Value = ... }" % fid)
            continue
        if inp.get("SourceOp") is not None:
            animated.append(fid)
            continue
        value = inp.get("Value")
        hit = ref["by_fusion"].get(fid)
        if hit is None or ref["inputs"][hit[0]].get("role") != "public":
            if report:
                report.unknown.append(fid)
            continue
        key, part = hit
        if part is None:
            values[key] = value
        else:
            partial.setdefault(key, {})[part] = value
    for key, parts in partial.items():
        base = list(ref["inputs"][key].get("default") or [0, 0, 0])
        for idx, v in parts.items():
            base[idx] = v
        values[key] = base
        if report and len(parts) < 3:
            missing = [ref["inputs"][key]["fusion"][i] for i in range(3) if i not in parts]
            report.note("%s: %s not written, so they take their defaults" % (key, ", ".join(missing)))
    return values, animated


def layout_block():
    """The UserControls block of Textizo3D's Fusion page layout (the Clipizo logo, the page tabs, a divider),
    as Fusion's Add Tool gives a new node; "" when the kit has no layout file."""
    try:
        with open(LAYOUT_PATH, "r", encoding="utf-8-sig") as handle:
            text = handle.read()
    except OSError:
        return ""
    start = text.find("UserControls = ordered()")
    if start < 0:
        return ""
    brace = text.find("{", start)
    depth, i = 0, brace
    in_str = False
    while i < len(text):
        c = text[i]
        if in_str:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    block = text[start:i + 1]
    # The layout file indents by two spaces a level and has UserControls three levels in, as here: tabs instead.
    lines = [line.strip("\r") for line in block.split("\n")]
    out = [lines[0]]
    for line in lines[1:]:
        stripped = line.lstrip(" ")
        indent = (len(line) - len(stripped)) // 2
        out.append("\t" * indent + stripped)
    return "\n".join(out)


def write_setting(values, ref, compact=False, with_layout=None):
    """Settings text for one Textizo3D node. Full: every input the kit knows (so Settings > Load onto a node
    gives exactly this); compact: only what differs from the defaults (for a pasted new node)."""
    base = defaults(ref)
    lines = []
    for key, entry in public_inputs(ref):
        value = values.get(key, base.get(key))
        always = key in ("Text", "Font", "Style")
        if compact and not always and same_value(value, base.get(key)):
            continue
        kind = entry.get("kind")
        if kind == "color":
            for fid, comp in zip(entry["fusion"], value):
                lines.append("\t\t\t\t%s = Input { Value = %s, }," % (fid, fmt_num(comp)))
        elif kind in ("text", "string", "file"):
            lines.append("\t\t\t\t%s = Input { Value = %s, }," % (key, lua_string(value if value is not None else "")))
        else:
            lines.append("\t\t\t\t%s = Input { Value = %s, }," % (key, fmt_num(value)))
    if with_layout is None:
        with_layout = not compact
    layout = layout_block() if with_layout else ""
    text = ["{", "\tTools = ordered() {", "\t\t%s = %s {" % (NODE_NAME, TOOL_TYPE), "\t\t\tInputs = {"]
    text += lines
    text += ["\t\t\t},", "\t\t\tViewInfo = OperatorInfo { Pos = { 0, 0 } },"]
    if layout:
        text.append("\t\t\t" + layout + ",")
    text += ["\t\t},", "\t},", '\tActiveTool = "%s"' % NODE_NAME, "}", ""]
    return "\n".join(text)


# --------------------------------------------------------------------------- spec -> values

def row_ids(side, row):
    base = "T3%s%s" % ("In" if side == "in" else "Out", ROW_KEYS[row])
    return base


def apply_row(values, ref, side, name, row, where, notes):
    key = ROW_ALIASES.get(norm_word(name), norm_word(name))
    if key not in ROW_KEYS:
        raise ValueError("%s: no row %r (rows: %s)" % (where, name, ", ".join(k for k, _ in ROWS)))
    if not isinstance(row, dict):
        raise ValueError("%s: a row is an object like {\"start\": 0, \"end\": 12, ...}" % where)
    unknown = set(row) - ROW_FIELDS
    if unknown:
        raise ValueError("%s: unknown fields %s (fields: %s)" % (where, ", ".join(sorted(unknown)), ", ".join(sorted(ROW_FIELDS))))
    base = row_ids(side, key)
    inputs = ref["inputs"]

    def put(suffix, value, label):
        rid = base + suffix
        if rid not in inputs:
            raise ValueError("%s: %s has no %s" % (where, key, label))
        values[rid] = coerce(rid, inputs[rid], value, "%s.%s" % (where, label), notes)

    put("On", bool(row.get("on", True)), "on")
    if "by" in row:
        put("Pieces", row["by"], "by")
    if "order" in row:
        put("Order", row["order"], "order")
    for field, suffix in (("start", "Start"), ("end", "End"), ("stagger", "Stagger"), ("ease", "Ease")):
        if field in row:
            put(suffix, row[field], field)
    for field, suffix in (("from", "From"), ("to", "To")):
        if field not in row:
            continue
        if side == "out" and field == "from":
            raise ValueError("%s: Out rows have no \"from\": they start from where the In row ended" % where)
        if key in AXIS_ROWS:
            vec = row[field]
            if is_number(vec):
                vec = [0, vec, 0] if key == "position" else [vec, 0, 0]
                notes.append("%s.%s: one number read as %s" % (where, field, vec))
            if not (isinstance(vec, (list, tuple)) and len(vec) == 3):
                raise ValueError("%s.%s: write [x, y, z]" % (where, field))
            for axis, v in zip("XYZ", vec):
                put(suffix + axis, v, "%s %s" % (field, axis))
        else:
            put(suffix, row[field], field)
    if key == "explosion":
        if "damping" in row:
            put("Damping", row["damping"], "damping")
        if "variance" in row:
            put("Variance", row["variance"], "variance")
        if "spin" in row:
            spin = row["spin"]
            if not (isinstance(spin, (list, tuple)) and len(spin) == 3):
                raise ValueError("%s.spin: write [x, y, z] in degrees" % where)
            for axis, v in zip("XYZ", spin):
                put("Spin" + axis, v, "spin " + axis)
        if "pre_roll" in row:
            put("PreRoll", row["pre_roll"], "pre_roll")
        if "reverse" in row:
            put("Reverse", bool(row["reverse"]), "reverse")
    else:
        for extra in ("damping", "variance", "spin", "pre_roll", "reverse"):
            if extra in row:
                raise ValueError("%s: %s is for the explosion row only" % (where, extra))


SPEC_KEYS = {"name", "look", "text", "font", "style", "inputs", "in", "out", "frames", "notes", "aspect"}


def spec_values(spec, ref, notes):
    """{input key: value} for a spec: the defaults (or a ready look's values), then the spec."""
    if not isinstance(spec, dict):
        raise ValueError("the spec is a JSON object")
    unknown = set(spec) - SPEC_KEYS
    if unknown:
        raise ValueError("unknown spec keys: %s (keys: %s)" % (", ".join(sorted(unknown)), ", ".join(sorted(SPEC_KEYS))))
    values = defaults(ref)
    if spec.get("look"):
        path = look_preset_path(spec["look"])
        if not path:
            raise ValueError("no ready look %r in presets/ (python tools/textizo3d_preset.py looks)" % spec["look"])
        with open(path, "r", encoding="utf-8-sig") as handle:
            tools, _, _ = find_tools(read_setting_text(handle.read()))
        look_values, _ = tool_values(tools[0][1], ref)
        values.update(look_values)
    inputs = ref["inputs"]
    for field, key in (("text", "Text"), ("font", "Font"), ("style", "Style")):
        if field in spec:
            values[key] = coerce(key, inputs[key], spec[field], field, notes)
    raw = spec.get("inputs") or {}
    if not isinstance(raw, dict):
        raise ValueError("inputs: an object like {\"Size\": 1.2}")
    for rid, value in raw.items():
        if rid in ref["by_fusion"] and ref["by_fusion"][rid][1] is not None:
            key, part = ref["by_fusion"][rid]
            if not is_number(value):
                raise ValueError("inputs.%s: needs a number from 0 to 1" % rid)
            values[key] = list(values[key])
            values[key][part] = float(value)
            continue
        entry = inputs.get(rid)
        if entry is None:
            close = suggest(rid, ref)
            hint = " (did you mean %s?)" % close if close else ""
            raise ValueError("inputs.%s: Textizo3D has no such input%s" % (rid, hint))
        if entry.get("role") != "public":
            raise ValueError("inputs.%s: not an input a preset sets (%s)" % (rid, entry.get("why", "internal")))
        values[rid] = coerce(rid, entry, value, "inputs.%s" % rid, notes)
    for side in ("in", "out"):
        rows = spec.get(side) or {}
        if not isinstance(rows, dict):
            raise ValueError("%s: an object of rows, like {\"blur\": {...}}" % side)
        for name, row in rows.items():
            apply_row(values, ref, side, name, row, "%s.%s" % (side, name), notes)
    return values


def look_preset_path(name):
    want = norm_word(os.path.splitext(os.path.basename(str(name)))[0])
    if os.path.isdir(PRESETS):
        for file_name in sorted(os.listdir(PRESETS)):
            if file_name.lower().endswith(".setting") and norm_word(os.path.splitext(file_name)[0]) == want:
                return os.path.join(PRESETS, file_name)
    return None


# --------------------------------------------------------------------------- values -> spec

def values_to_spec(values, ref, name=None):
    """A spec (as build takes it) with what differs from Textizo3D's defaults."""
    base = defaults(ref)
    spec = {}
    if name:
        spec["name"] = name
    spec["text"] = values.get("Text", base["Text"])
    spec["font"] = values.get("Font", base["Font"])
    spec["style"] = values.get("Style", base["Style"])
    row_inputs = set()
    for side in ("in", "out"):
        rows = {}
        for key, _ in ROWS:
            rid = row_ids(side, key)
            ids = [k for k in ref["inputs"] if k.startswith(rid) and ref["inputs"][k].get("role") == "public"]
            on = values.get(rid + "On", 0)
            if not on:
                continue
            row_inputs.update(ids)
            row = {}
            entry = ref["inputs"]

            def opt(rid_, field):
                if rid_ in entry:
                    row[field] = norm_option(entry[rid_], values.get(rid_, base.get(rid_)))

            def num(rid_, field):
                if rid_ in entry:
                    row[field] = values.get(rid_, base.get(rid_))

            opt(rid + "Pieces", "by")
            opt(rid + "Order", "order")
            num(rid + "Start", "start")
            num(rid + "End", "end")
            num(rid + "Stagger", "stagger")
            if key in AXIS_ROWS:
                if side == "in":
                    row["from"] = [values.get(rid + "From" + a, base.get(rid + "From" + a)) for a in "XYZ"]
                row["to"] = [values.get(rid + "To" + a, base.get(rid + "To" + a)) for a in "XYZ"]
            else:
                if side == "in":
                    num(rid + "From", "from")
                num(rid + "To", "to")
            opt(rid + "Ease", "ease")
            if key == "explosion":
                num(rid + "Damping", "damping")
                num(rid + "Variance", "variance")
                row["spin"] = [values.get(rid + "Spin" + a, base.get(rid + "Spin" + a)) for a in "XYZ"]
                num(rid + "PreRoll", "pre_roll")
                row["reverse"] = bool(values.get(rid + "Reverse", 0))
            rows[key] = row
        if rows:
            spec[side] = rows
    inputs = {}
    for key, entry in public_inputs(ref):
        if key in ("Text", "Font", "Style") or key in row_inputs:
            continue
        value = values.get(key, base.get(key))
        if same_value(value, base.get(key)):
            continue
        if entry.get("kind") == "choice":
            inputs[key] = entry["options"][int(value)]
        elif entry.get("kind") == "checkbox":
            inputs[key] = bool(value)
        elif entry.get("kind") == "color":
            inputs[key] = [round(float(c), 6) for c in value]
        else:
            inputs[key] = value
    if inputs:
        spec["inputs"] = inputs
    return spec


def spec_json(spec):
    """A spec as JSON text, with short lists of numbers ([r, g, b], [x, y, z]) on one line."""
    text = json.dumps(spec, indent=2, ensure_ascii=False)
    return re.sub(r"\[\s*((?:-?[\d.eE+-]+,\s*)*-?[\d.eE+-]+)\s*\]",
                  lambda m: "[" + ", ".join(p.strip() for p in m.group(1).split(",")) + "]", text) + "\n"


def norm_option(entry, value):
    """A choice's label in the spec's spelling: "Out Cubic" -> "out_cubic"."""
    options = entry.get("options") or []
    idx = int(value) if is_number(value) else 0
    label = options[idx] if 0 <= idx < len(options) else str(value)
    return re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")


# --------------------------------------------------------------------------- check

class Report:
    def __init__(self):
        self.errors, self.warnings, self.notes, self.info, self.unknown = [], [], [], [], []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def note(self, msg):
        self.notes.append(msg)


def check_value(key, entry, value):
    """None when `value` fits the input, else a short reason."""
    kind = entry.get("kind")
    if kind == "color":
        if not (isinstance(value, list) and len(value) == 3 and all(is_number(v) for v in value)):
            return "needs three numbers (red, green, blue)"
        return None
    if kind in ("text", "string", "file"):
        return None if isinstance(value, str) else 'needs text in quotes, like "Hello"'
    if not is_number(value):
        return "needs a number"
    if kind == "checkbox" and value not in (0, 1):
        return "is a checkbox: use 0 or 1"
    if kind == "choice":
        options = entry.get("options") or []
        if not float(value).is_integer() or not 0 <= value < len(options):
            return "must be one of 0..%d (%s)" % (len(options) - 1, ", ".join("%d %s" % (i, o) for i, o in enumerate(options)))
    if kind == "integer" and not float(value).is_integer():
        return "needs a whole number"
    lo, hi = entry.get("min"), entry.get("max")
    if (lo is not None and value < lo) or (hi is not None and value > hi):
        return "must be between %s and %s" % (fmt_num(lo) if lo is not None else "-inf", fmt_num(hi) if hi is not None else "inf")
    return None


def text_pieces(text):
    """Letters, words and lines as Textizo3D counts them: every non-blank character is a letter."""
    letters = words = lines = 0
    in_word = in_line = False
    for ch in text:
        blank = ch in " \t\r\n"
        if ch == "\n":
            in_line = False
        if blank:
            in_word = False
            continue
        if not in_word:
            words += 1
            in_word = True
        if not in_line:
            lines += 1
            in_line = True
        letters += 1
    return letters, words, lines


def row_timing(values, side, key, counts):
    """(pieces, frames each piece moves, frames between pieces) of an on row, by the engine's formula."""
    rid = row_ids(side, key)
    mode = int(values.get(rid + "Pieces", 0))
    order = int(values.get(rid + "Order", 0))
    n = max(counts[min(max(mode, 0), 2)], 1)
    if order in (2, 3):
        r_max = math.floor((n - 1) / 2.0)
    else:
        r_max = n - 1
    k = max(float(values.get(rid + "Stagger", 0)), 0.0) / 100.0
    length = max(float(values.get(rid + "End", 0)) - float(values.get(rid + "Start", 0)), 1.0)
    each = length / (1 + k * r_max)
    return n, each, k * each


def estimate_width(values, ref, aspect):
    """The longest line's width as a share of the frame's width (a rough estimate), or None."""
    text = values.get("Text") or ""
    font = (values.get("Font") or "").lower()
    caps, small = DEFAULT_WIDTH
    for name, w in sorted(FONT_WIDTH.items(), key=lambda kv: -len(kv[0])):
        if font == name or font.startswith(name + " "):
            caps, small = w
            break
    style = (values.get("Style") or "").lower()
    if "condensed" in style or "condensed" in font:
        caps, small = caps * 0.8, small * 0.8
    size = float(values.get("Size", 1))
    tracking = float(values.get("Tracking", 1))
    widest = 0.0
    for line in text.split("\n"):
        w = 0.0
        for ch in line:
            arial = ARIAL_WIDTHS.get(ch)
            if ch.isalpha() and ch.islower():
                w += small * (arial / AVG_SMALL if arial else 1.0)
            else:
                w += caps * (arial / AVG_CAPS if arial else 1.0)
        widest = max(widest, w)
    half = widest * size * tracking / 2
    dist = max(float(values.get("T3CamDistance", 4.8)) - float(values.get("PositionZ", 0)), 0.1)
    fov = math.radians(min(max(float(values.get("T3CamFov", 30)), 1), 170))
    # Seen at an angle (the camera's Orbit against the text's Rotation Y), the nearer end comes closer and looks
    # bigger: that end decides whether the line fits.
    theta = math.radians(min(abs(float(values.get("T3CamOrbit", -18)) - float(values.get("RotationY", 0))), 80))
    near = half * math.cos(theta) * dist / max(dist - half * math.sin(theta), 0.1 * dist)
    near += abs(float(values.get("PositionX", 0)))
    visible_half = dist * math.tan(fov / 2) * aspect
    return near / visible_half if visible_half > 0 else None


def check_values(values, ref, report, frames=None, aspect=16 / 9.0, written=None):
    inputs = ref["inputs"]
    for key, value in values.items():
        entry = inputs.get(key)
        if entry is None:
            continue
        why = check_value(key, entry, value)
        if why:
            report.error("%s %s (it is %r)" % (key, why, value))
            continue
        if entry.get("kind") in ("number", "integer") and entry.get("slider"):
            lo, hi = entry["slider"]
            span = hi - lo
            if span > 0 and (value < lo - span or value > hi + span):
                report.note("%s = %s is far outside its slider (%s to %s): allowed, but check it" % (
                    key, fmt_num(value), fmt_num(lo), fmt_num(hi)))
    text = values.get("Text", "")
    if written is not None and "Text" not in written:
        report.warn('no Text: the node shows "%s", the default text' % inputs["Text"]["default"])
    if not str(text).strip():
        report.warn("the Text is empty: nothing is drawn")
    letters, words, lines = text_pieces(str(text))
    font, style = values.get("Font", ""), values.get("Style", "")
    report.info.append(("text", "%s (%d letters, %d words, %d lines), %s %s, Size %s" % (
        json.dumps(text, ensure_ascii=False), letters, words, lines, font, style, fmt_num(values.get("Size", 1)))))
    bundled = {(f["family"].lower(), f["style"].lower()) for f in ref.get("fonts", [])}
    families = {f["family"].lower() for f in ref.get("fonts", [])}
    if font and font.lower() not in families and font.lower() not in SYSTEM_FONTS:
        report.note("the font %r is neither carried by Textizo3D nor on every computer: it must be installed "
                    "where the video renders, or the text falls back to another font" % font)
    elif font.lower() in families and (font.lower(), style.lower()) not in bundled:
        report.note("Textizo3D carries %s, but not as %r: the nearest weight it has is used" % (font, style))

    # Material summary.
    face, side = values.get("FaceColor"), values.get("SideColor")
    metal, rough = float(values.get("T3Metal", 0)), float(values.get("T3Roughness", 0.35))
    finish = "metal" if metal >= 0.5 else "plastic"
    finish = ("mirror " if rough < 0.12 else "glossy " if rough < 0.3 else "satin " if rough < 0.55 else "matte ") + finish
    look = "%s, faces %s, sides %s" % (finish, color_hex(face), color_hex(side)) if face and side else finish
    for key, label in (("FaceTexture", "face texture"), ("SideTexture", "side texture"), ("EnvImage", "environment image"),
                       ("FaceShader", "face shader"), ("SideShader", "side shader"), ("EnvShader", "environment shader")):
        if values.get(key):
            look += ", %s %s" % (label, values[key])
    if float(values.get("T3Glow", 0)) > 0:
        look += ", glow %s" % fmt_num(values["T3Glow"])
    if float(values.get("T3EdgeGlow", 0)) > 0:
        look += ", edge glow %s" % fmt_num(values["T3EdgeGlow"])
    report.info.append(("look", look))

    # Pictures and shaders.
    textures = set(ref.get("textures", []))
    for key in ("FaceTexture", "SideTexture", "EnvImage"):
        path = values.get(key) or ""
        if not path:
            continue
        if is_relative(path):
            if norm_path(path) not in {norm_path(t) for t in textures}:
                report.warn("%s %r: Textizo3D carries no such texture (python tools/textizo3d_preset.py textures)" % (key, path))
        else:
            report.note("%s is the user's own file %r: it must exist at that path on the computer that renders" % (key, path))
    for key in ("FaceShader", "SideShader", "EnvShader"):
        path = values.get(key) or ""
        if not path:
            continue
        report.note("%s %r: a shader file must exist at that path; Shader Status on the Textures page shows whether "
                    "it compiled. A slow shader slows every frame" % (key, path))
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as handle:
                    if "mainImage" not in handle.read():
                        report.error("%s %r has no mainImage(out vec4, in vec2) function" % (key, path))
            except OSError:
                pass

    # Rows and timing.
    counts = (letters, words, lines)
    clip = frames
    on_rows = {"in": [], "out": []}
    for side in ("in", "out"):
        parts = []
        for key, _ in ROWS:
            rid = row_ids(side, key)
            if not values.get(rid + "On"):
                continue
            start, end = int(values.get(rid + "Start", 0)), int(values.get(rid + "End", 0))
            on_rows[side].append((key, start, end))
            n, each, gap = row_timing(values, side, key, counts)
            by = ref["inputs"][rid + "Pieces"]["options"][int(values.get(rid + "Pieces", 0))].lower()
            order = ref["inputs"][rid + "Order"]["options"][int(values.get(rid + "Order", 0))]
            ease = ref["inputs"][rid + "Ease"]["options"][int(values.get(rid + "Ease", 0))]
            parts.append("%s %s %d-%d (%d %s, %s, each %s frames, %s apart, %s)" % (
                key, by, start, end, n, by, order, fmt_num(round(each, 1)), fmt_num(round(gap, 1)), ease))
            if end <= start:
                report.warn("%s %s: End Frame %d is not after Start Frame %d (it plays as one frame)" % (side, key, end, start))
            if clip and end > clip - 1:
                report.warn("%s %s ends on frame %d, after the clip's last frame %d" % (side, key, end, clip - 1))
            if side == "in" and end - start > 45:
                report.note("in %s takes %d frames: Textizo3D looks best with fast reveals (8 to 24 frames)" % (key, end - start))
            if key == "position" and side == "in":
                dist = math.sqrt(sum((float(values.get(rid + "From" + a, 0)) - float(values.get(rid + "To" + a, 0))) ** 2 for a in "XYZ"))
                if dist > 0.35:
                    report.note("in position moves the letters %s units: long slides are off the house style "
                                "(a blur-in, a size pop or a flip read better)" % fmt_num(round(dist, 2)))
        report.info.append((side, "; ".join(parts) if parts else "no rows on"))
    if on_rows["in"] and on_rows["out"]:
        last_in = max(e for _, _, e in on_rows["in"])
        first_out = min(s for _, s, _ in on_rows["out"])
        if first_out < last_in:
            report.warn("the Out rows start (frame %d) before the In rows end (frame %d)" % (first_out, last_in))
        elif first_out - last_in < 12:
            report.note("the text holds only %d frames between In and Out" % (first_out - last_in))
    if clip and not on_rows["out"]:
        pass
    moving = any(k in ("position", "rotation", "size", "explosion") for side in on_rows for k, _, _ in on_rows[side])
    if moving and not values.get("MotionBlur"):
        report.note("fast moves look smoother with MotionBlur 1 (Camera page)")

    # Layout.
    share = estimate_width(values, ref, aspect)
    if share is not None:
        pct = "more than 300%" if share > 3 else "about %d%%" % round(share * 100)
        report.info.append(("frame", "the longest line fills %s of the frame's width (a rough estimate, "
                                     "on its nearer side)" % pct))
        if share > 1.0:
            report.warn("the longest line may not fit the frame (%s of its width): lower Size, use a narrower "
                        "font, more lines, or a smaller Orbit" % pct)
        elif share > 0.85:
            report.note("the longest line comes close to the frame's edge (about %d%% of its width)" % round(share * 100))


def suggest(name, ref, fusion=False):
    """The public input closest to a misspelled one ("FaceColour" -> FaceColor), or None."""
    names = [k for k, e in ref["inputs"].items() if e.get("role") == "public"]
    if fusion:
        names += [fid for fid, (key, part) in ref["by_fusion"].items() if part is not None]
    exact = [k for k in names if norm_word(k) == norm_word(name)]
    lower = {k.lower(): k for k in names}
    close = exact[:1] or [lower[c] for c in difflib.get_close_matches(name.lower(), list(lower), n=1, cutoff=0.75)]
    if not close:
        return None
    best = close[0]
    if fusion and ref["inputs"].get(best, {}).get("kind") == "color":
        return "%s (three inputs)" % ", ".join(ref["inputs"][best]["fusion"])
    return best


def is_relative(path):
    return not (os.path.isabs(path) or re.match(r"^[A-Za-z]:[\\/]", path) or path.startswith("\\\\") or path.startswith("/"))


def norm_path(path):
    return path.replace("\\", "/").lower().lstrip("./")


def check_text(text, ref, frames=None, aspect=16 / 9.0):
    """(report, tool name, input count, others) for settings text; raises ValueError when unreadable."""
    root = read_setting_text(text)
    tools, splines, others = find_tools(root)
    if not tools:
        raise ValueError("no %s node in the file" % TOOL_TYPE)
    report = Report()
    name, tool = tools[0]
    if len(tools) > 1:
        report.note("the file has %d Textizo3D nodes; only %s was checked" % (len(tools), name))
    inputs = tool.get("Inputs")
    if not isinstance(inputs, Table):
        raise ValueError("%s has no Inputs = { ... }" % name)
    for dup in inputs.duplicates:
        report.error("%s is written twice" % dup)
    values, animated = tool_values(tool, ref, report)
    for fid in report.unknown:
        entry = ref["inputs"].get(fid)
        if fid == "Look":
            pass
        elif entry is not None and entry.get("role") == "ui":
            report.error("%s is a menu that depends on the computer's fonts: leave it out and write Font and Style" % fid)
        elif fid in ("inspector_page",):
            pass
        elif entry is not None:
            report.error("%s is not an input a preset sets: leave it out" % fid)
        else:
            close = suggest(fid, ref, fusion=True)
            report.error("%s is not a Textizo3D input%s: Resolve ignores it" % (
                fid, " (did you mean %s?)" % close if close else ""))
    if "Look" in inputs.fields:
        report.warn("Look is written: loaded onto a node it applies that ready look over these values. Leave it out "
                    "(the values are all here)")
    for fid in animated:
        report.note("%s is keyframed (from Resolve): kept as it is, not checked" % fid)
    full = defaults(ref)
    full.update(values)
    check_values(full, ref, report, frames, aspect, written=set(values))
    count = len(inputs.fields)
    return report, name, count, others


def print_report(path, report, tool_name=None, count=None, others=None):
    print("Textizo3D preset check: %s" % os.path.basename(path))
    if tool_name:
        print("  node: %s, %d inputs" % (tool_name, count))
    for name, kind in others or []:
        print("  other node in the file: %s (%s)" % (name, kind))
    for key, text in report.info:
        print("  %-6s %s" % (key + ":", text))
    for title, items in (("ERRORS", report.errors), ("WARNINGS", report.warnings), ("NOTES", report.notes)):
        if items:
            print("%s (%d):" % (title, len(items)))
            for item in items:
                print("  - " + item)
    ok = not report.errors
    print("Result: %s (%d errors, %d warnings)" % ("OK" if ok else "FAILED", len(report.errors), len(report.warnings)))
    return ok


# --------------------------------------------------------------------------- commands

SHORT_NAME_RE = re.compile(r"^(?:textizo3d(?:fx)?[-_ ]?)?(\d{1,3})([a-z])$", re.I)
SHORT_FILE_RE = re.compile(r"^Textizo3D-(\d{2,3})([A-Z])\.setting$", re.I)


def preset_file_name(name):
    name = (name or "").strip()
    m = SHORT_NAME_RE.match(name)
    if m:
        return "%s-%02d%s.setting" % (PREFIX, int(m.group(1)), m.group(2).upper())
    if not name:
        return PREFIX + "-01A.setting"
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    return (name if name.lower().startswith("textizo3d") else PREFIX + " - " + name) + ".setting"


def used_preset_names(folders):
    used = {}
    for folder in folders:
        if os.path.isdir(folder):
            for file_name in os.listdir(folder):
                m = SHORT_FILE_RE.match(file_name)
                if m:
                    used.setdefault(int(m.group(1)), set()).add(m.group(2).upper())
    return used


def resolve_settings_dir():
    home = os.path.expanduser("~")
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or os.path.join(home, "AppData", "Roaming")
        return os.path.join(base, "Blackmagic Design", "DaVinci Resolve", "Support", "Fusion", "Settings")
    if sys.platform == "darwin":
        return os.path.join(home, "Library", "Application Support", "Blackmagic Design", "DaVinci Resolve", "Fusion", "Settings")
    return os.path.join(home, ".local", "share", "DaVinciResolve", "Fusion", "Settings")


def downloads_dir():
    return os.path.join(os.path.expanduser("~"), "Downloads", "Textizo3D Presets")


def target_folder(target):
    named = {"resolve": resolve_settings_dir(), "downloads": downloads_dir()}
    return os.path.expanduser(named.get(target, target))


def bundle_resources():
    """Textizo3D's installed Resources folder on this computer, or None."""
    candidates = []
    if sys.platform.startswith("win"):
        common = os.environ.get("CommonProgramFiles") or r"C:\Program Files\Common Files"
        candidates.append(os.path.join(common, "OFX", "Plugins", "Textizo3D.ofx.bundle", "Contents", "Resources"))
    elif sys.platform == "darwin":
        candidates.append("/Library/OFX/Plugins/Textizo3D.ofx.bundle/Contents/Resources")
    else:
        candidates.append("/usr/OFX/Plugins/Textizo3D.ofx.bundle/Contents/Resources")
    for path in candidates:
        if os.path.isdir(path):
            return path
    return None


def cmd_next_name(args):
    folders = [MY_PRESETS, PRESETS] + [target_folder(t) for t in args.to or []]
    used = used_preset_names(folders)
    if args.variant is not None:
        free = [ch for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if ch not in used.get(args.variant, set())]
        if not free:
            print("all letters of %02d are used; start a new number" % args.variant)
            return 1
        print("%s-%02d%s" % (PREFIX, args.variant, free[0]))
        return 0
    print("%s-%02dA" % (PREFIX, max(used) + 1 if used else 1))
    return 0


def load_spec(path):
    with open(path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def build_text(spec, ref, compact=False):
    notes = []
    values = spec_values(spec, ref, notes)
    return write_setting(values, ref, compact=compact), notes


def cmd_build(args):
    ref = load_reference()
    try:
        spec = load_spec(args.spec)
    except json.JSONDecodeError as exc:
        print("spec error: invalid JSON at line %d, column %d: %s (look for a missing or extra comma or quote)" % (
            exc.lineno, exc.colno, exc.msg))
        return 1
    try:
        text, notes = build_text(spec, ref, compact=args.compact)
    except ValueError as exc:
        print("spec error: %s" % exc)
        return 1
    out_path = args.out or os.path.join(MY_PRESETS, preset_file_name(spec.get("name")))
    inside_work = os.path.normcase(os.path.abspath(out_path)).startswith(os.path.normcase(MY_PRESETS) + os.sep)
    if os.path.exists(out_path) and not (args.overwrite or inside_work):
        print("%s already exists; pass --overwrite to replace it (files in my-presets/ are replaced without asking)" % out_path)
        return 1
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    print("wrote %s" % out_path)
    frames = args.frames or spec.get("frames")
    aspect = spec.get("aspect") or 16 / 9.0
    report, name, count, others = check_text(text, ref, frames, aspect)
    for note in notes:
        report.note(note)
    if not SHORT_FILE_RE.match(os.path.basename(out_path)) and not args.out:
        report.note("presets get short names: Textizo3D-<number><letter>, for example Textizo3D-07A "
                    "(python tools/textizo3d_preset.py next-name --to <folder>)")
    ok = print_report(out_path, report, name, count, others)
    return 0 if ok else 1


def cmd_check(args):
    ref = load_reference()
    all_ok = True
    for path in args.files:
        try:
            with open(path, "r", encoding="utf-8-sig", errors="replace") as handle:
                report, name, count, others = check_text(handle.read(), ref, args.frames, args.aspect)
        except (OSError, ValueError) as exc:
            print("Textizo3D preset check: %s\nERRORS (1):\n  - %s\nResult: FAILED\n" % (os.path.basename(path), exc))
            all_ok = False
            continue
        all_ok = print_report(path, report, name, count, others) and all_ok
        print()
    return 0 if all_ok else 1


def setting_to_spec(text, ref, name=None):
    tools, _, _ = find_tools(read_setting_text(text))
    if not tools:
        raise ValueError("no %s node in the file" % TOOL_TYPE)
    values, animated = tool_values(tools[0][1], ref)
    full = defaults(ref)
    full.update(values)
    spec = values_to_spec(full, ref, name)
    if animated:
        spec["notes"] = "keyframed in Resolve (not in this spec): " + ", ".join(animated)
    return spec


def cmd_to_spec(args):
    ref = load_reference()
    try:
        with open(args.file, "r", encoding="utf-8-sig", errors="replace") as handle:
            spec = setting_to_spec(handle.read(), ref, os.path.splitext(os.path.basename(args.file))[0])
    except (OSError, ValueError) as exc:
        print("error: %s" % exc)
        return 1
    text = spec_json(spec)
    if args.out:
        if os.path.exists(args.out) and not args.overwrite and not os.path.normcase(os.path.abspath(args.out)).startswith(
                os.path.normcase(MY_PRESETS) + os.sep):
            print("%s already exists; pass --overwrite to replace it" % args.out)
            return 1
        with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        print("wrote %s" % args.out)
    else:
        sys.stdout.write(text)
    return 0


def cmd_looks(_args):
    ref = load_reference()
    looks = ref.get("looks", [])
    if not looks:
        print("no ready looks listed in reference/inputs.json")
        return 1
    for look in looks:
        spec_path = os.path.join(KIT, "specs", look["name"] + ".json")
        about = look.get("about", "")
        if not about and os.path.isfile(spec_path):
            about = load_spec(spec_path).get("notes", "")
        print("%-15s Look menu %d  %s" % (look["name"], look["index"], about))
    return 0


def cmd_textures(_args):
    ref = load_reference()
    textures = ref.get("textures", [])
    where = bundle_resources()
    if not textures:
        print("this version of Textizo3D carries no textures (use the user's own images by their full path)")
    for item in textures:
        print(item)
    if textures and where:
        print("\non this computer they are in %s" % where)
    return 0


def cmd_where(_args):
    for label, path in (("resolve", resolve_settings_dir()), ("downloads", downloads_dir())):
        print("%-9s %s  (%s)" % (label, path, "exists" if os.path.isdir(path) else "will be created"))
    where = bundle_resources()
    print("%-9s %s" % ("plugin", where or "Textizo3D is not installed in the usual place on this computer"))
    return 0


def cmd_install(args):
    ref = load_reference()
    target = target_folder(args.to)
    status = 0
    for path in args.files:
        try:
            with open(path, "r", encoding="utf-8-sig", errors="replace") as handle:
                report, _, _, _ = check_text(handle.read(), ref)
        except (OSError, ValueError) as exc:
            print("not installed: %s (%s)" % (path, exc))
            status = 1
            continue
        if report.errors:
            print("not installed: %s has errors; run the check command" % path)
            status = 1
            continue
        os.makedirs(target, exist_ok=True)
        dest = os.path.normpath(os.path.join(target, os.path.basename(path)))
        if os.path.exists(dest) and not args.overwrite:
            print("not installed: %s already exists (pass --overwrite or use the next free name)" % dest)
            status = 1
            continue
        shutil.copyfile(path, dest)
        print("installed: %s" % dest)
    return status


def main(argv=None):
    parser = argparse.ArgumentParser(description="Textizo3D preset helper: build, check, to-spec, looks, textures, where, next-name, install.")
    sub = parser.add_subparsers(dest="command")
    p = sub.add_parser("build", help="write a preset from a JSON spec, then check it")
    p.add_argument("spec")
    p.add_argument("out", nargs="?", help="default: my-presets/<name>.setting")
    p.add_argument("--frames", type=int, help="clip length in frames, to warn about rows that run past it")
    p.add_argument("--compact", action="store_true", help="write only what differs from the defaults, without the Fusion page layout")
    p.add_argument("--overwrite", action="store_true")
    p.set_defaults(func=cmd_build)
    p = sub.add_parser("check", help="check presets")
    p.add_argument("files", nargs="+")
    p.add_argument("--frames", type=int, help="clip length in frames")
    p.add_argument("--aspect", type=float, default=16 / 9.0, help="frame width / height (0.5625 for 9:16)")
    p.set_defaults(func=cmd_check)
    p = sub.add_parser("to-spec", help="turn a preset into a JSON spec")
    p.add_argument("file")
    p.add_argument("out", nargs="?")
    p.add_argument("--overwrite", action="store_true")
    p.set_defaults(func=cmd_to_spec)
    p = sub.add_parser("looks", help="list the ready looks")
    p.set_defaults(func=cmd_looks)
    p = sub.add_parser("textures", help="list the textures Textizo3D carries")
    p.set_defaults(func=cmd_textures)
    p = sub.add_parser("where", help="print the folders presets can go to")
    p.set_defaults(func=cmd_where)
    p = sub.add_parser("next-name", help="the next free short preset name, like Textizo3D-07A")
    p.add_argument("--to", action="append", help="also look in resolve, downloads or a folder (repeat for several)")
    p.add_argument("--variant", type=int, help="number of an existing look: print its next free letter instead")
    p.set_defaults(func=cmd_next_name)
    p = sub.add_parser("install", help="copy checked presets to a folder")
    p.add_argument("files", nargs="+")
    p.add_argument("--to", required=True, help="resolve, downloads, or a folder path")
    p.add_argument("--overwrite", action="store_true")
    p.set_defaults(func=cmd_install)
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    if not getattr(args, "func", None):
        parser.print_help()
        return 2
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
