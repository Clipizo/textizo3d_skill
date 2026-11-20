# Textizo3DFX AI Kit

Let your AI make **Textizo3DFX** looks: 3D text for DaVinci Resolve's Fusion page, ready to paste. Describe what you want in plain words, for example *"a chrome title that blurs in"*, *"gold 'LEVEL UP' seen from below"* or *"a glowing neon sign"*. The AI writes the node, checks it, and saves it where you want.

This kit is made for Textizo3DFX (Clipizo); `reference/inputs.json` names the version it was built from. Textizo3DFX must be installed.

## Two ways to use it

**1. With any AI chat** (ChatGPT, Claude, Gemini, Copilot):

1. Give the chat the file **`Textizo3DFX AI Guide.md`**.
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
| Resolve's Settings folder | The look is listed in a Textizo3DFX node's right-click **Settings** menu, and **Settings > Load…** opens this folder. |
| Downloads/Textizo3DFX Presets | Easy to find. Drag a look onto the Nodes area, or load it with Settings > Load…. |
| Any folder you name | |

Resolve's Settings folder is in these places:

- **Windows:** `%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Settings`
- **Mac:** `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Settings`
- **Linux:** `~/.local/share/DaVinciResolve/Fusion/Settings`

## What is inside

| File or folder | Contents |
|---|---|
| `Textizo3DFX AI Guide.md` | Everything an AI needs to know about Textizo3DFX's text, animation, materials, lights, camera, textures and shaders. |
| `SKILL.md`, `AGENTS.md` | Instructions for AI agents. `CLAUDE.md` and `GEMINI.md` point to them. |
| `presets/` | Textizo3DFX's ready looks (the Look menu's), each as a node with every value written out. |
| `specs/` | The same looks as short, editable descriptions. |
| `tools/textizo3dfx_preset.py` | Builds, checks and installs looks. Needs Python 3 and nothing else. |
| `reference/inputs.json` | The list of Textizo3DFX's controls, fonts and textures, which the checker uses. `reference/fusion-layout.setting`: the node's Fusion page tabs. |
| `my-presets/` | Where the agent keeps your looks while it works on them. |

The ready looks:

<!-- looks -->
| Look | Look menu | What it is |
|---|---|---|
| Textizo3D-01A | 1 | Game Show: glossy green faces, green sides, plastic, worn (dents and scratches), edge glow, glow, shadow on the wall, no animation |
<!-- /looks -->

New looks get short names like `Textizo3D-07A`: a number for each look and a letter for each variation.

## Using a look in Resolve

- **As a new node:** on the Fusion page, paste the code into the Nodes area, or drag the `.setting` file onto it. Connect the node to MediaOut1, or Merge it over your clip.
- **On an existing Textizo3DFX node:** right-click the node and choose **Settings > Load…**.
- **Your own text:** type it in the Inspector afterwards. The animation follows any length of text.

## License

Free of charge, under the Clipizo product license in `LICENSE.txt`. Use the kit and its looks in your own projects, personal or commercial, including client work and monetized videos. Please don't re-upload or redistribute the files; to recommend Textizo3DFX, link to its page on clipizo.com.
