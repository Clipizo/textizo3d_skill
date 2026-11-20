---
name: textizo3d-looks
description: Makes ready-to-paste Textizo3D 3D text nodes (.setting files) for DaVinci Resolve's Fusion page from a plain description (for example "a chrome title", "gold text that blurs in letter by letter", "a neon sign", "glossy red letters that pop in"). It checks each node and saves it where the user wants, including Resolve's own Settings folder. Use it whenever the user asks for a Textizo3D title, 3D text look or 3D text animation, or for changes to one.
---

# Textizo3D looks

You make looks for **Textizo3D**, a 3D text plugin for DaVinci Resolve. A look is a small `.setting` text file holding one Textizo3D node with its text, font, material, lights, camera and animation. The user pastes it into the Fusion page (or drags the file onto the Nodes area, or loads it onto a Textizo3D node). Nothing here is for the Edit page.

## Before you start

- **Read `Textizo3D AI Guide.md` completely, once per session.** It is the reference for:
  - the text, fonts and what fits in the frame (section 3);
  - the animation rows and their timing (sections 4 to 6);
  - shape, material, camera, light, textures and shaders (sections 7 to 11);
  - the house style and the material recipes (section 12), the ready looks (section 13);
  - every control and its default (section 14), and how users load a node (section 17).

  This file only adds the workflow for agents that can use files.
- **The helper** is `python tools/textizo3d_preset.py` (use `python3` on Mac and Linux, or `py` on some Windows installs). It needs Python 3 and nothing else. It reads `reference/inputs.json`, the list of Textizo3D's controls.
- **If Python is not available,** write the node by hand from the guide's examples (sections 15 and 16) and go through the guide's checklist yourself.

## Workflow

1. **Understand the request.** Ask, in one message and only for what is missing:
   - the text;
   - the look or mood (chrome, gold, neon, glossy, worn, a texture...), colours or font (optional);
   - whether it moves, and the clip's length and frame rate (default: still, 5 s at 24 fps);
   - whether it goes over footage.

   Use the house style from guide section 12 unless the user wants something else.
2. **Ask where to save** (once per session; remember the answer), unless the user already named a folder. Show the real paths from `python tools/textizo3d_preset.py where`. The options:
   1. **Resolve's Settings folder** (recommended). Looks there appear in a Textizo3D node's right-click **Settings** menu, and **Settings > Load…** opens that folder.
      - Windows: `%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Settings`
      - Mac: `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Settings`
   2. **Downloads/Textizo3D Presets.** Easy to find. The user drags a file onto the Nodes area.
   3. **A folder the user names.**
   4. **Both 1 and 2.**
3. **Pick a short name.** Looks are named `Textizo3D-` plus a two-digit number and a capital letter, for example `Textizo3D-07A`.
   - The number is the look. Get the next free one with `python tools/textizo3d_preset.py next-name --to resolve` (use the user's folder choice). It starts after the ready looks in `presets/`.
   - The letter is a variation of that look. Get the next letter with `next-name --to resolve --variant 7`, which gives `Textizo3D-07B`. A variation of a ready look (for example `Textizo3D-01A` in gold) takes that look's number: `next-name --variant 1`.
   - Use no spaces and no descriptive words in the name. Describe the look in your message instead.
4. **Write a spec.** Start from the closest file in `specs/` (one for each ready look in `presets/`; `python tools/textizo3d_preset.py looks` lists them), or from `"look"` plus your changes, and save it as `my-presets/<short name>.json`. The format is below.
5. **Build and check:**
   ```
   python tools/textizo3d_preset.py build "my-presets/Textizo3D-07A.json" --frames <clip length in frames>
   ```
   This writes `my-presets/Textizo3D-07A.setting`: a complete node (every control written out, so loading it onto an existing node gives exactly this look, plus the Fusion page tabs). Rebuilding replaces files in `my-presets/` without asking: it is the kit's work folder. Files in the folder the user chose are never replaced without asking (step 6).

   The report shows the text, the material, every row's frames (how long each piece moves and how far apart they start) and an estimate of how much of the frame's width the text takes. You cannot see the render, so take its warnings seriously.
   - Fix every **ERROR**.
   - Fix every **WARNING** unless the user asked for that.
   - **NOTES** are house-style hints (guide section 12); follow them unless the request says otherwise.
6. **Install:**
   ```
   python tools/textizo3d_preset.py install "my-presets/Textizo3D-07A.setting" --to resolve
   ```
   Use `--to downloads` or `--to "<folder>"` for the other choices. The command refuses to overwrite an existing file; ask the user whether to replace it (`--overwrite`) or use the next free name.
7. **Tell the user:**
   - the look's short name, what it looks like and how it moves;
   - where the file is;
   - how to use it (guide section 17): drag it onto the Fusion page's Nodes area (or Settings > Load… on a Textizo3D node), then connect it to MediaOut1 or through a Merge;
   - that they can type their own text in the Inspector, and how to move the exit for a longer clip.

   They have the file, so do not paste the node's text unless they ask for it. You cannot see the result, so describe it, and never claim you have tested it in Resolve.
8. **Change it on feedback.** A fix to the same look keeps its name: edit the spec, rebuild, and reinstall with `--overwrite`. When the user wants to keep both versions, give the new one the next letter.

You can also start from a node the user saved from Resolve, or any `.setting`: `python tools/textizo3d_preset.py to-spec "<file.setting>" my-presets/Textizo3D-07A.json`.

For a chat answer (no files), `build --compact` writes only what differs from Textizo3D's defaults, like the guide's examples, without the page tabs. Compact nodes are for pasting as a new node.

## Spec format

```json
{
  "name": "Textizo3D-07A",
  "look": "Textizo3D-01A",
  "text": "GAME\nOVER",
  "font": "Anton",
  "style": "Regular",
  "inputs": {
    "Size": 1.2,
    "FaceColor": "#FFDB80",
    "SideColor": [0.9, 0.62, 0.2],
    "T3Metal": 1,
    "T3Roughness": 0.15,
    "T3FloorMode": "Shadow Only",
    "FaceTexture": "textures/<file>",
    "MotionBlur": true
  },
  "in": {
    "blur":    {"by": "letters", "order": "left_to_right", "start": 0, "end": 14, "stagger": 60, "from": 0.1, "to": 0, "ease": "out_cubic"},
    "opacity": {"by": "letters", "order": "left_to_right", "start": 0, "end": 12, "stagger": 60, "from": 0, "to": 1, "ease": "out_quad"}
  },
  "out": {
    "opacity": {"by": "words", "start": 104, "end": 116, "stagger": 0, "to": 0, "ease": "in_cubic"}
  },
  "frames": 120
}
```

**Top level:**

- `name`: the short name, for example `Textizo3D-07A` (`07A` works too); the file becomes `Textizo3D-07A.setting`.
- `look`: optional, a ready look in `presets/` to start from (its values first, then yours). Without it, the spec starts from Textizo3D's defaults.
- `text`, `font`, `style`: as in guide section 3. `\n` makes a new line.
- `inputs`: any input of guide section 14 by its ID: numbers, `true`/`false` for checkboxes, a dropdown's number or its option's name (`"Shadow Only"`, `"Out Back"`), text in quotes. A colour is its ID without Red/Green/Blue (`"FaceColor"`) with `"#RRGGBB"` or `[r, g, b]` from 0 to 1; the single channels (`"FaceColorRed"`) work too. Only IDs whose `role` is `public` in `reference/inputs.json`.
- `in`, `out`: the animation rows (below).
- `keys`: the viewer's keyframes of the whole text (guide section 6, "Viewer keyframes"): a list like `[{"frame": 0, "position": [-3, 0, 0], "ease": "out_back"}, {"frame": 18, "position": [0, 0, 0]}]`, each with `frame` (from the clip's first frame) and any of `position` (`[x, y, z]`), `size`, `rotation` (`[x, y, z]` degrees) and `ease` (a row ease's name, `hold`, or `"cubic-bezier(x1, y1, x2, y2)"` for a curve of your own); fields left out keep the node's values. `keys_base` is rarely needed (the guide says when).
- `frames`: the clip length, used by the check (the same as `--frames`). `aspect`: the frame's width / height for the fit estimate (0.5625 for 9:16). `notes`: ignored; use it for your own comments.

**Rows** (the keys of `in` and `out`): `opacity`, `blur`, `position`, `size`, `tracking`, `rotation`, `explosion`. Each row you list is turned on (write `"on": false` to turn off a row a look has). Fields:

- `by`: `letters`, `words` or `lines`.
- `order`: `left_to_right`, `right_to_left`, `center_out`, `edges_in`, `random_one_by_one` or `random`.
- `start`, `end`: frames from the clip's first frame; `stagger`: percent (guide section 5).
- `from` (In rows only) and `to`: numbers, or `[x, y, z]` for `position` (units) and `rotation` (degrees).
- `ease`: `linear`, `in_quad` ... `out_back`, `out_elastic`, `out_bounce` (guide section 6), or the row's own curve, `"cubic-bezier(x1, y1, x2, y2)"`.
- Explosion only: `damping`, `variance`, `spin` (`[x, y, z]` degrees), `pre_roll` (frames), `reverse` (`true`/`false`).

Fields you leave out keep the look's (or the default) value.

## Other commands

```
python tools/textizo3d_preset.py build "<spec.json>" ["<out.setting>"] [--frames N] [--compact] [--overwrite]
python tools/textizo3d_preset.py check "<file.setting>" [--frames N] [--aspect 0.5625]
python tools/textizo3d_preset.py to-spec "<file.setting>" [out.json]
python tools/textizo3d_preset.py keys "<file.setting>"
python tools/textizo3d_preset.py looks
python tools/textizo3d_preset.py textures
python tools/textizo3d_preset.py where
python tools/textizo3d_preset.py next-name --to resolve [--variant 7]
```

`build` with an output path outside `my-presets/` refuses to replace an existing file unless you pass `--overwrite`.

## Textures and shaders

- `python tools/textizo3d_preset.py textures` lists the textures Textizo3D carries. Write them as `textures/<file>`: they work on every computer with Textizo3D.
- The user's own images are full paths with forward slashes; ask for the path, never invent one.
- For a shader (guide section 11), write the `.glsl` file into `my-presets/` and the folder the user chose, and point `FaceShader`, `SideShader` or `EnvShader` at its full path in that folder. Tell the user the shader file must stay there.

## Rules

- **Only write to `my-presets/` and the folder the user chose.** Never delete files. Outside `my-presets/`, never overwrite a file without asking.
- **Leave the kit unchanged** (`presets/`, `specs/`, `reference/`, `tools/`, the guide, this file) unless the user asks.
- **Use short names:** `Textizo3D-07A.setting`, with a new number for each look and a new letter for each variation. Never use spaces or descriptive words in the name.
- **Never guess input IDs.** Use the guide, or `reference/inputs.json` with `role: public`. Never write `Look`, `FontMenu` or `StyleMenu`.
- **Keep the text the user's:** their words, spelling and capitals.
- **If a new look does not appear in the right-click Settings menu**, tell the user to use Settings > Load… (or drag the file onto the Nodes area, or restart Resolve).
