# Textizo3D AI Kit

Let your AI make **Textizo3D** looks: 3D text for DaVinci Resolve's Fusion page, ready to paste. Describe what you want in plain words, for example *"a chrome title that blurs in"*, *"gold 'LEVEL UP' seen from below"* or *"a glowing neon sign"*. The AI writes the node, checks it, and saves it where you want.

This kit is made for Textizo3D (Clipizo); `reference/inputs.json` names the version it was built from. Textizo3D must be installed.

## Two ways to use it

**1. With any AI chat** (ChatGPT, Claude, Gemini, Copilot):

1. Give the chat the file **`Textizo3D AI Guide.md`**.
2. Describe the 3D text you want.
3. Copy the code it gives you, click in Fusion's Nodes area, and press Ctrl+V (Mac: Cmd+V).

The guide's first section explains this step by step.

**2. With an AI agent that can open folders** (Claude Code, OpenAI Codex, Gemini CLI, Cursor, VS Code with Copilot):

1. Open this folder in the agent.
2. Ask for a look.

The agent reads `AGENTS.md` and `SKILL.md`, asks you a few questions (including where to save), then writes and checks the `.setting` file.

For Claude, you can also upload this folder, zipped, as a custom skill.

## Where looks can go

| Choice | What you get |
|---|---|
| Resolve's Settings folder | The look is listed in a Textizo3D node's right-click **Settings** menu, and **Settings > Load…** opens this folder. |
| Downloads/Textizo3D Presets | Easy to find. Drag a look onto the Nodes area, or load it with Settings > Load…. |
| Any folder you name | |

Resolve's Settings folder is in these places:

- **Windows:** `%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Settings`
- **Mac:** `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Settings`
- **Linux:** `~/.local/share/DaVinciResolve/Fusion/Settings`

## What is inside

| File or folder | Contents |
|---|---|
| `Textizo3D AI Guide.md` | Everything an AI needs to know about Textizo3D's text, animation, materials, lights, camera, textures and shaders. |
| `SKILL.md`, `AGENTS.md` | Instructions for AI agents. `CLAUDE.md` and `GEMINI.md` point to them. |
| `presets/` | Textizo3D's ready looks (the Look menu's), each as a node with every value written out. |
| `specs/` | The same looks as short, editable descriptions. |
| `tools/textizo3d_preset.py` | Builds, checks and installs looks. Needs Python 3 and nothing else. |
| `reference/inputs.json` | The list of Textizo3D's controls, fonts and textures, which the checker uses. `reference/fusion-layout.setting`: the node's Fusion page tabs. |
| `my-presets/` | Where the agent keeps your looks while it works on them. |

The ready looks:

<!-- looks -->
| Look | Look menu | What it is |
|---|---|---|
| Textizo3D-01A | 1 | Money: glossy green with dents and scratches, a green edge glow and bloom, a soft shadow on a wall behind. |
| Textizo3D-02A | 2 | Ice: chunky letters of clear cyan ice, white caustics inside, a thick rounded bevel, cool bloom. |
| Textizo3D-03A | 3 | Lava: chunky lumpy letters of marbled molten lava, self-lit, a yellow edge glow, a deep rounded bevel. |
| Textizo3D-04A | 4 | Sky chrome: white chrome faces, the sky's blue in the chamfer and the sides, deep extrusion, low camera. |
| Textizo3D-05A | 5 | Gold: bright yellow-gold faces, darker brown-gold sides, a hard chamfer catching the light, low camera. |
| Textizo3D-06A | 6 | Brushed steel: pale blue-grey brushed faces, near-black steel sides, low camera. |
| Textizo3D-07A | 7 | Game-show names: glossy light-blue plastic, deeper blue sides, deep extrusion, soft light from the top. |
| Textizo3D-08A | 8 | Money, green: glossy bright green, a dark green extrusion as its outline, a green-lit top, a green bloom. |
| Textizo3D-09A | 9 | Money, red: glossy red faces with a crisp white stroke, a red-brown extrusion. |
| Textizo3D-10A | 10 | Gold numbers: pale-to-deep yellow faces on a deep navy extrusion, star glints. |
| Textizo3D-11A | 11 | Pearl puff: inflated italic letters, pearly white-blue faces, blue rims, white specular streaks. |
| Textizo3D-12A | 12 | Bandana: black paisley print on each letter, black sides, a fiery rim and fire light from below. |
| Textizo3D-13A | 13 | Leopard: leopard print on the faces, dark brown sides, fire light from below. |
| Textizo3D-14A | 14 | Fight poster: worn white print, a shallow dark-red extrusion, a red glow from below, a soft shadow behind. |
| Textizo3D-15A | 15 | Arena chrome: silver letters lit by a ring's red and blue lights, a red edge glow. |
<!-- /looks -->

New looks get short names like `Textizo3D-07A`: a number for each look and a letter for each variation.

## Using a look in Resolve

- **As a new node:** on the Fusion page, paste the code into the Nodes area, or drag the `.setting` file onto it. Connect the node to MediaOut1, or Merge it over your clip.
- **On an existing Textizo3D node:** right-click the node and choose **Settings > Load…**.
- **Your own text:** type it in the Inspector afterwards. The animation follows any length of text.

## License

Free of charge, under the Clipizo product license in `LICENSE.txt`. Use the kit and its looks in your own projects, personal or commercial, including client work and monetized videos. Please don't re-upload or redistribute the files; to recommend Textizo3D, link to its page on clipizo.com.
