# Textizo3D AI Guide

For **Textizo3D** (Clipizo), the 3D text plugin for DaVinci Resolve: extruded, bevelled letters with real materials, lights, shadows, reflections, glows, textures and shaders, and per-letter animation. Give this file to any AI chat, such as ChatGPT, Claude, Gemini or Copilot, and it can write a ready-to-paste Textizo3D node for Resolve's Fusion page. Textizo3D is available at clipizo.com.

---

## Quick start (for you)

1. **Give this file to your AI.** Open the chat and attach this file (or paste all of its text). Then say what you want. For example: *"Make a Textizo3D title: 'GAME OVER' in shiny gold, letters blurring in one by one, for a 5-second clip at 24 fps."*
2. **Copy the code.** The AI answers with one block of code. Copy all of it; most chats have a Copy button on the block.
3. **Paste it into Resolve.** On the **Fusion** page, click an empty spot in the **Nodes** area and press **Ctrl+V** (Mac: **Cmd+V**). A new Textizo3D node appears with your 3D text.
4. **Connect it.**
   - For the text on its own, connect the Textizo3D node to **MediaOut1**.
   - For the text over a video clip, add a **Merge** node: connect MediaIn1 to the Merge's yellow background input, Textizo3D to its green foreground input, and the Merge to MediaOut1.

You can change the text, font and everything else in the Inspector at any time.

**To keep a look for later**, ask the AI for a `.setting` file, or save the code in a plain text file with the short name the AI gave it, for example `Textizo3D-07A.setting`. Drag that file onto the Nodes area to add it again, or put it in Resolve's Settings folder (section 17).

Textizo3D must be installed (version 1.0 or later). On the Edit page, Textizo3D also works as a clip of its own (Effects > OpenFX > Generators > Clipizo > Textizo3D) with its **Look** menu; this guide is for the Fusion page node.

---

## Instructions for the AI

You are making a **Textizo3D node**: plain text in Fusion's settings format that the user pastes into Resolve's Fusion page or saves as a `.setting` file. Everything you need is in this guide. **Only use input names (IDs) that appear in this guide (section 14), and do not guess others.** A misspelled ID, or an ID in the wrong capitals, is silently ignored by Resolve.

**How to answer:**

1. **Ask only if something essential is missing,** in one short message. The text is the only thing worth a question. For everything else, reuse what the user said earlier, or use these defaults: 24 fps and a 5-second clip (frames 0 to 119), a 16:9 frame, the default camera, and no animation unless the user asks for movement. Say in your reply which defaults you used.
2. **Pick the look from the request** (sections 8 to 12): a material (chrome, gold, glossy plastic, neon, matte, worn metal, textured), a font (section 3), and, if asked, an entrance and an exit (sections 4 and 5). Start from the closest example (sections 15 and 16) or recipe (section 12).
3. **Reply in three parts:**
   - one or two sentences describing the look and its animation, starting with the node's short name in bold, like **Textizo3D-07A**;
   - the whole node in **one** code block marked `lua`, with nothing else in it;
   - the usage steps from section 17 (paste, connect, type your own text), in 3 or 4 short lines.
4. **Give every look a short name:** `Textizo3D-` followed by a two-digit number and a capital letter, for example `Textizo3D-07A`.
   - The ready looks in Textizo3D's Look menu use the first numbers (section 13). Start new looks after them.
   - A variation of a look keeps its number and takes the next letter (`Textizo3D-07B`, `Textizo3D-07C`).
   - Use no spaces and no descriptive words in the name; describe the look in your reply instead.
   - If the user mentions looks they already have, continue after their highest number.

   If your chat can attach files, also attach the node as a file named after it, for example `Textizo3D-07A.setting`. If it cannot, add one line telling the user they can save the code in a text file with that name to keep it.
5. **When the user asks for changes,** send the whole node again, not just the changed lines.
6. **You cannot see the result.** Describe what the look should do, never claim you have tested it, and keep text inside the frame with the rules in section 3.

**Checklist (check every item before you answer):**

- [ ] **One node, written exactly like the examples.** The text is `{ Tools = ordered() { Textizo3D1 = ofx.com.clipizo.textizo3dfx { Inputs = { ... }, ViewInfo = OperatorInfo { Pos = { 0, 0 } }, }, }, ActiveTool = "Textizo3D1" }` with exactly one node. No comments.
- [ ] **Always write `Text`, `Font` and `Style`.** `Font` and `Style` are the font's family and style names (section 3). Never write `FontMenu`, `StyleMenu` or `Look`.
- [ ] **Colours are three inputs**, each from 0 to 1: `FaceColorRed`, `FaceColorGreen`, `FaceColorBlue` (and the same for every colour in section 14).
- [ ] **Animation rows:** a row moves only with its `...On` input at 1. For every row you turn on, write its frames, values, `Pieces`, `Order` and `Ease` wherever they differ from the row's defaults (section 14: In rows run from frame 0 to 30, Out rows from 90 to 115). Frames are whole numbers and every row ends before the clip's last frame.
- [ ] **Values are in range:** checkboxes are 0 or 1, dropdowns use the numbers in section 14, and decimals use a dot.
- [ ] **Text fits:** the longest line's width follows section 3's rule for the font and Size.
- [ ] **Files:** textures Textizo3D carries are written `textures/<file>` (section 11); other images and shaders are full paths with forward slashes, and the user must have that file.
- [ ] **Each ID once.** Do not write the same input twice.
- [ ] **Name:** the node has a short name like `Textizo3D-07A` (step 4 above).

---

## 1. How Textizo3D works

Textizo3D is an OpenFX plugin that draws its own 3D scene on the graphics card: the text as solid letters with a front face, sides and bevels; a camera; a key light with soft shadows, fill, ambient and under lights; reflections of an environment; and 2D glows on top. On the Fusion page it is a node (`Textizo3D1`) that needs no input: it draws at the composition's frame size, with a transparent background around the letters. Its optional input is a background: an image connected there is drawn behind the text.

Its Inspector has eight pages: **Text, In, Out, Shape, Material, Camera, Light, Textures**. On the Fusion page a node pasted from a chat switches pages with its **Page** menu at the top; a node built by the kit's tool, or added with Add Tool, shows the Clipizo logo and page tabs instead.

The **Look** menu on the Text page applies a ready look (section 13) and keeps the text. A node you write carries every value itself, so it never uses that menu.

Every animation is per letter, word or line: each page (In, Out) has seven rows (Opacity, Blur, Position, Size, Tracking, Rotation, Explosion) that move the pieces in turn. Textizo3D starts with every row off: a still 3D title. Turn rows on only when the user wants movement.

## 2. The preset file

A preset is Fusion settings text. Every input is written like this:

```
				<InputID> = Input { Value = <value>, },
```

Value formats:

| Kind | Write it as | Example |
|---|---|---|
| number | a plain decimal number (use a dot, not a comma) | `1.25`, `-18`, `0` |
| whole number (frames, counts) | digits only | `12` |
| checkbox | 0 or 1 | `T3InBlurOn = Input { Value = 1, },` |
| dropdown | the option's number, from 0 (section 14) | `T3FloorMode = Input { Value = 1, },` is Shadow Only |
| text | in double quotes. Write a new line as `\n`, a quote as `\"`, and a backslash as `\\` | `"GAME\nOVER"` |
| colour | three inputs, red, green and blue, from 0 to 1 | `FaceColorRed`, `FaceColorGreen`, `FaceColorBlue` |
| file | a path in double quotes, with forward slashes | `"textures/<file>"`, `"C:/Users/me/Pictures/marble.jpg"` |

The order of the inputs does not matter.

**What happens to inputs you leave out:**

- A node **pasted as a new node** takes Textizo3D's defaults (section 14) for anything you leave out. The examples are written that way: they list `Text`, `Font`, `Style` and what differs from the defaults.
- A preset **loaded onto an existing node** (Settings > Load…) keeps that node's old values for anything left out. Presets built by the kit's tool write every input, so loading one gives exactly that look.

**Never write** `Look` (it would apply a ready look over your values when the node is loaded), `FontMenu` or `StyleMenu` (their numbers depend on each computer's fonts; Textizo3D sets them from `Font` and `Style` by itself).

## 3. Text, font and placement (Text page)

- `Text`: the words. Use `\n` for a new line. Keep it short: titles of one to four words look best in 3D.
- `Font`, `Style`: the font's family and style names exactly as installed, for example `"Anton"` and `"Regular"`, `"Montserrat"` and `"Black"`. Textizo3D carries the fonts listed below, so they work on every computer; so do the fonts every Windows and Mac computer has (Arial, Arial Black, Impact, Georgia, Times New Roman, Verdana, Trebuchet MS, Courier New, Tahoma). Any other font must be installed where the video renders. A style the family lacks draws in its nearest weight; a missing family draws in Arial Black, then Arial.
- `Size` (default 1): the letters' height. One unit is the font's full height (ascent plus descent); capitals are about half a unit tall.
- `Tracking` (default 1): multiplies the space each letter takes. 0.85 to 0.95 tightens heavy fonts.
- `LineSpacing` (default 1): lines are 0.826 × Size × Line Spacing apart.
- `Alignment`: 0 left, 1 centre (default), 2 right. The block is centred on the middle of the frame.
- `PositionX`, `PositionY`, `PositionZ`: move the whole text, in units (Y up, Z toward the camera).
- `RotationX`, `RotationY`, `RotationZ`: turn the whole text, in degrees (X tips it back, Y turns it, Z rolls it).

**Fonts Textizo3D carries** (family: styles):

<!-- fonts -->
- **Anton**: Regular
- **Archivo Black**: Regular
- **Bangers**: Regular
- **Barlow**: Regular, Bold, Black
- **Bebas Neue**: Regular
- **Fredoka**: Light, Regular, Medium, SemiBold, Bold
- **Inter**: Thin, ExtraLight, Light, Regular, Medium, SemiBold, Bold, ExtraBold, Black
- **Kanit**: Regular, Bold, Black
- **Luckiest Guy**: Regular
- **Montserrat**: Thin, ExtraLight, Light, Regular, Medium, SemiBold, Bold, ExtraBold, Black
- **Nunito**: ExtraLight, Light, Regular, Medium, SemiBold, Bold, ExtraBold, Black
- **Open Sans**: Light, Regular, SemiBold, Bold, ExtraBold, Condensed Light, Condensed Regular, Condensed SemiBold, Condensed Bold, Condensed ExtraBold
- **Oswald**: ExtraLight, Light, Regular, Medium, SemiBold, Bold
- **Permanent Marker**: Regular
- **Poppins**: Regular, SemiBold, Bold, Black
- **Roboto**: Thin, ExtraLight, Light, Regular, Medium, SemiBold, Bold, ExtraBold, Black, Condensed Thin, Condensed ExtraLight, Condensed Light, Condensed Regular, Condensed Medium, Condensed SemiBold, Condensed Bold, Condensed ExtraBold, Condensed Black
- **Rubik**: Light, Regular, Medium, SemiBold, Bold, ExtraBold, Black
- **Vazirmatn**: Thin, ExtraLight, Light, Regular, Medium, SemiBold, Bold, ExtraBold, Black
<!-- /fonts -->

**Letters are drawn one by one, left to right.** Latin, Cyrillic, Greek and other scripts whose letters stand alone work. Scripts whose letters join or run right to left (Arabic, Persian, Hebrew, Hindi) don't draw correctly. Use a font that has every character in the text.

**Will it fit?** With the default camera, a 16:9 frame is about 4.6 units wide where the text stands. The text's width is about Size × Tracking × the sum of its letters' widths. A capital takes, at Size 1: Anton or Bebas Neue 0.33, Oswald 0.38, Impact 0.44, Bangers 0.43, Kanit 0.45, Poppins 0.51, Barlow 0.52, Arial Black 0.56, Roboto 0.57, Inter 0.59, Luckiest Guy 0.61, Montserrat or Rubik 0.63, Archivo Black 0.72 (small letters about 15% less). The camera looks from the side (`T3CamOrbit` -18), so the nearer end looks bigger: keep the line under about 85% of the width. In short, at Size 1 with the default camera:

| Font | Capitals that fit on a line |
|---|---|
| Anton, Bebas Neue | about 11 |
| Impact, Bangers, Kanit | about 8 |
| Arial Black, Poppins, Inter | about 6 to 7 |
| Montserrat, Archivo Black | about 5 to 6 |

For longer text, lower `Size` (Size 0.6 fits about 1.7 times as many letters), split it into lines, or move the camera back (`T3CamDistance`).

## 4. Animation rows (In and Out pages)

Each page has seven rows. Every row has an ID start, written here as `<row>`:

| Row | In ID start | Out ID start | What moves | Value with the row off |
|---|---|---|---|---|
| Opacity | `T3InOpacity` | `T3OutOpacity` | see-through (0) to solid (1) | 1 |
| Blur | `T3InBlur` | `T3OutBlur` | blur of each piece: 0.1 is soft, 0.2 very soft (0.25 at most) | 0 |
| Position | `T3InPos` | `T3OutPos` | offset X, Y, Z in units | 0, 0, 0 |
| Size | `T3InSize` | `T3OutSize` | size about each piece's centre (1 = normal) | 1 |
| Tracking | `T3InTrack` | `T3OutTrack` | the space each letter takes, added to 1: 0 is normal, 2 three times as wide (the letters spread apart) | 0 |
| Rotation | `T3InRot` | `T3OutRot` | turn about each piece's centre, X, Y, Z in degrees | 0, 0, 0 |
| Explosion | `T3InExplode` | `T3OutExplode` | distance each piece flies, each in its own random direction | 0 |

A row's inputs (add the ending to its ID start, for example `T3InBlur` + `On` = `T3InBlurOn`):

| Ending | Meaning |
|---|---|
| `On` | 1 turns the row on. A row that is off does nothing, whatever its other values. |
| `Pieces` | what moves: 0 letters, 1 words, 2 lines |
| `Order` | 0 left to right, 1 right to left, 2 centre out, 3 edges in, 4 random one by one, 5 random |
| `Start`, `End` | the row's first and last frame, counted from the clip's first frame (frame 0) |
| `Stagger` | how the pieces follow each other, in percent (section 5) |
| `From` | In rows only: the start value. Position and Rotation have `FromX`, `FromY`, `FromZ`. |
| `To` | the end value. Position and Rotation have `ToX`, `ToY`, `ToZ`. |
| `Ease` | the motion's curve (section 6) |

An In row moves each piece from its `From` value to its `To` value. An Out row has no `From`: it moves each piece from where the In row left it (or from the value with the row off) to its `To` value. So an In Opacity row 0 → 1 and an Out Opacity row → 0 fade the text in and out.

The Explosion row has more: `Damping` (0 to 8: slows the end of the flight), `Variance` (0 to 1: pieces at different speeds), `SpinX`, `SpinY`, `SpinZ` (degrees each piece turns while flying), `PreRoll` (frames: starts the flight that many frames before `Start`) and `Reverse` (1: the pieces go in reverse order; on the In page they also fly out instead of in).

Common rows:

- **Blur-in reveal:** Blur from 0.1 to 0 with Opacity from 0 to 1, by letters, left to right, Out Cubic and Out Quad. Each letter takes 4 to 8 frames and starts 1 to 2 frames after the one before (section 5): for 8 letters, Stagger 25 and End = Start + 8 + 2 × 7 = Start + 22.
- **Pop:** Size from 0 (or 0.6) to 1, Out Back (or Out Elastic for a wobble), with a quick Opacity row.
- **Flip up:** Rotation `FromX` 90 to 0 with Opacity, Out Cubic.
- **Close in:** Tracking from 1.5 to 0 by letters, centre out, Out Cubic, with Opacity.
- **Assemble:** Explosion from 1.5 to 0 with Opacity, Out Cubic; out: Explosion to 1.5 with Opacity to 0, In Cubic.
- **Exit:** Opacity to 0 with Blur to 0.1, by words, In Cubic, 8 to 12 frames before the clip ends.

## 5. Timing

Frames count from the clip's first frame (0). A 5-second clip at 24 fps has frames 0 to 119; at 30 fps, 0 to 149. Work out frames from the clip's length and frame rate; when you don't know them, use 24 fps and 120 frames and say so.

How a row spreads over its pieces (N letters, words or lines; spaces and line breaks don't count):

- `End - Start` is the whole row: the first piece starts at `Start`, the last ends at `End`.
- With `Stagger` 0 all pieces move together. With `Stagger` 100 each starts when the one before ends. In between they overlap.
- Each piece moves for **S = (End - Start) / (1 + k × R)** frames, where k = Stagger / 100 and R = N - 1 (for centre out and edges in, R = the whole part of (N - 1) / 2). Piece number r (0, 1, 2, …) starts at **Start + r × k × S**.
- **To give each piece `span` frames and a `gap` between their starts:** Stagger = 100 × gap / span and End = Start + span + gap × R. For "HELLO" (5 letters, R = 4), span 8 and gap 2: Stagger 25, End = Start + 16.

The text holds still between the In rows' last frame and the Out rows' first frame. Textizo3D reuses that still frame instead of drawing it again (`T3HoldStill`, on by default).

## 6. Eases

`Ease` takes a number: 0 Linear; 1 In Quad, 2 Out Quad, 3 In Out Quad; 4 In Cubic, 5 Out Cubic, 6 In Out Cubic; 7 In Quart, 8 Out Quart, 9 In Out Quart; 10 In Quint, 11 Out Quint, 12 In Out Quint; 13 In Sine, 14 Out Sine, 15 In Out Sine; 16 In Expo, 17 Out Expo, 18 In Out Expo; 19 In Circ, 20 Out Circ, 21 In Out Circ; 22 In Back, 23 Out Back, 24 In Out Back; 25 In Elastic, 26 Out Elastic, 27 In Out Elastic; 28 In Bounce, 29 Out Bounce, 30 In Out Bounce.

Out eases (2, 5, 8, 17) suit entrances: fast, then settling. In eases (1, 4) suit exits. Out Back (23) overshoots a little: good for pops. Out Elastic (26) and Out Bounce (29) wobble: sticker style.

## 7. Shape

- `ExtrusionDepth` (default 0.25): how deep the letters are, in units. 0.3 to 0.4 looks bold; 0.1 is a thin plate.
- `BevelDepth`, `BevelWidth` (default 0.015): the rounded or chamfered edge around the front face. 0.03 catches more light (chrome, gold); 0 is a sharp edge. Thin fonts take small bevels.
- `FrontBevel`, `BackBevel`: which edges get the bevel (1 = yes).
- `SmoothingAngle` (default 30): corners sharper than this stay sharp; corners softer than it are shaded smooth.

## 8. Material

- `FaceColor`: the front faces. `SideColor`: the sides and bevels. A darker or more saturated side colour gives depth.
- `T3Roughness` (0 mirror to 1 matte, default 0.35) and `T3Metal` (0 plastic to 1 metal): metal takes its colour into its reflections (gold, chrome, copper); plastic reflects white highlights over its colour.
- `T3Coat` (default 0.4) with `T3CoatRough` (0.06): a clear varnish on top that adds a sharp gloss, even on rough or coloured plastic. `T3Specular` (Reflectivity, default 1): the strength of non-metal reflections.
- `T3Emission` (0 to 1): the colour glows by itself, without light. Use it for neon (with the Glow).
- **Wear:** `T3Bump` (face dents, 0 to 1), `T3Scratches` (fine grooves, 0 to 1), `T3Smudges` (patchy roughness, default 0.15). Details: `T3BumpStyle` (0 hammered dimples, 1 smooth lumps), `T3BumpSize`, `T3BumpDetail`, `T3SideBump`, and the scratches' count, length, width, angle and seed.
- **Glow** (2D, over the picture): `T3Glow` (0 to 3) blooms everything brighter than `T3GlowThreshold` (0 to 1), spread by `T3GlowSize` (default 20; sizes are for a 1920-wide frame and scale with it). `T3EdgeGlow` (0 to 3) draws a glowing line along every front face's edge in `EdgeColor`, `T3EdgeWidth` thousandths of the frame's width wide, softened by `T3EdgeSoft`. Glows add light; where there are no letters that light carries its own opacity (its brightest channel), so it shows on Resolve's Edit page and over video.
- **Effects** (the Material page's Effects section; every one off by default, animated by the clip's time, light added like the glows):
  - **Beyond the Letters** (`T3FxBeyond`, default 1): the effects spread round the letters (flames rise above them, mist sinks below). 0 keeps every effect inside the letters' shapes (letters filled with fire, frost or sparkles).
  - **Fire** (`T3FireOn` 1): flames rising from the letters, drawn behind them, and embers drifting up. `T3FireFlames` (0 to 2, default 1; 0 leaves only embers), `T3FireHeight` (0 to 3, default 1: about a fifth of the frame's height), `T3FireEmbers` (0 to 3, default 1, how many sparks), `T3FireSpeed` (default 1), `FireColor` (the flames' main colour, default orange 1, 0.42, 0.06; their cores are hotter, their tips deeper). Made for the lava look (Textizo3D-03A); embers alone (`T3FireFlames` 0) suit the fight-night looks.
  - **Frost** (`T3FrostOn` 1): cold mist sinking off the letters and snowflakes drifting down. `T3FrostMist` (0 to 2, 0 leaves only snow), `T3FrostHeight` (how far mist and snow fall), `T3FrostSnow` (0 to 3, how many flakes), `T3FrostSpeed`, `FrostColor` (default 0.75, 0.92, 1). Made for the ice look (Textizo3D-02A); also cold chrome.
  - **Sparkles** (`T3SparkleOn` 1): four-point star glints twinkling on the letters. `T3SparkleAmount` (0 to 3), `T3SparkleSize` (0 to 3), `T3SparkleSpeed` (twinkle speed), `SparkleColor` (warm 1, 0.88, 0.55 on gold; icy 0.8, 0.95, 1 on ice). For gold, chrome, diamond, pearl and money.
  - Effects make every frame move, so they are drawn frame by frame (Reuse Still Frames can't hold them); a 1080p frame costs about 2 ms more.

## 9. Camera

- `T3CamDistance` (default 4.8) and `T3CamFov` (field of view, default 30): a closer camera with a wider field (3.2 and 45) exaggerates the perspective for a heroic look.
- `T3CamOrbit` (default -18): the camera turned around the text, in degrees. 0 looks straight on.
- `T3CamTilt` (default 10): above (positive) or below (negative) the text. -12 to -16 looks up at it, which makes it feel big.
- `T3CamTargetY`: the height the camera looks at.
- `T3CamDrift` (degrees) and `T3CamPush` (percent): a slow orbit and push-in over the whole clip. They make every frame different, so the still frames are drawn every time.
- **Render Quality:** `MotionBlur` (1 smooths fast moves; `BlurQuality` samples, default 4; `ShutterAngle` default 180), `EdgeSmoothing` (1 off, 2 four samples (default), 3 to 8 eight samples), `T3HoldStill` (keep it 1).

## 10. Light, shadows and reflections

- **Key light:** `T3KeyIntensity` (default 0.9), `KeyColor`, `T3KeyAngle` (around, default -35), `T3KeyHeight` (up, default 40), `T3KeySpread` (cone, default 70), `T3KeyFalloff` (its edge's softness). It casts the shadows.
- **Shadows:** `T3Shadows` (1 on), `T3FloorMode` and `T3WallMode` (0 off, 1 Shadow Only, 2 Visible), `T3ShadowDarkness` (default 0.6), `T3ShadowSoftness` (default 0.015). Shadow Only is an invisible floor or wall that shows only the shadow: it grounds the text over footage. Visible draws the plane in `FloorColor` or `WallColor`. `T3FloorGap` and `T3WallDistance` place them.
- **Fill and ambient:** `T3FillIntensity` (default 0.25) with `FillColor` and `T3FillAngle`; `T3AmbientIntensity` (default 0.2); `T3UnderIntensity` (0) with `UnderColor`, a light from below (good with a camera looking up).
- **Reflections:** `T3EnvIntensity` (default 1) sets how much of the environment the letters reflect. The environment is a vertical gradient from `EnvironmentBottom` to `EnvironmentTop` with bright vertical light strips (`T3Strips` brightness, `T3StripCount`, `T3StripWidth`), turned by `T3EnvRotation`. This gradient shows only in reflections; it doesn't light the letters. An Environment Image or Shader (section 11) also lights them softly. Metal looks best with bright strips over a dark bottom.

## 11. Textures and shaders

- `FaceTexture`, `SideTexture`: an image multiplied into the face or side colour. With a white colour the image shows as it is; where the image is transparent, the plain colour shows. PNG, JPG, TGA, BMP, PSD, GIF and HDR work.
- `TexMapping`: 0 the image spans the whole text, 1 each word, 2 each letter. `TexScale` (default 1): repeats across that area (2 = twice). Side textures run along each letter's outline (one repeat per capital's height) and across the depth.
- `EnvImage`: a 2:1 panorama (equirectangular, HDR or JPG/PNG) the letters reflect and are lit by, in place of the gradient and strips. `T3EnvRotation` turns it.

**Textures Textizo3D carries.** Write them as `textures/<file>`: Textizo3D finds them inside its own installation, on every computer.

<!-- textures -->
- `textures/camo.jpg`
- `textures/carbon-fiber.jpg`
- `textures/diamond-glitter.jpg`
- `textures/distressed-white.jpg`
- `textures/env-arena.hdr`
- `textures/env-sky.hdr`
- `textures/env-studio.hdr`
- `textures/env-sunset.hdr`
- `textures/gold-brushed.jpg`
- `textures/gold-glitter.jpg`
- `textures/gold-gradient.jpg`
- `textures/ice-caustics.jpg`
- `textures/ice.jpg`
- `textures/lava-molten.jpg`
- `textures/lava.jpg`
- `textures/leopard.jpg`
- `textures/paisley.jpg`
- `textures/silver-brushed.jpg`
<!-- /textures -->

**The user's own images** are full paths with forward slashes, for example `"C:/Users/me/Pictures/marble.jpg"` (Windows) or `"/Users/me/Pictures/marble.jpg"` (Mac). The file must exist at that path on the computer that renders. Ask the user for the path; never invent one.

**Shaders.** `FaceShader`, `SideShader` and `EnvShader` take a Shadertoy-style GLSL file (GLSL 3.30, `texture()` not `texture2D()`) with this function:

```glsl
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / iResolution.xy;
    float s = 0.5 + 0.5 * sin(6.2831853 * (uv.x * 3.0 + uv.y * 1.5 - iTime * 0.5));
    vec3 a = vec3(1.0, 0.25, 0.55);
    vec3 b = vec3(0.2, 0.6, 1.0);
    fragColor = vec4(mix(a, b, smoothstep(0.35, 0.65, s)), 1.0);
}
```

- It gets `iResolution` (1024 × 1024 for the face and side shaders, 512 × 256 for the environment), `iTime` (seconds from the clip's first frame × `ShaderSpeed`), `iTimeDelta`, `iFrame`, `iFrameRate`, `iDate`, `iMouse` (always 0), `iChannel0` (the matching image: Face Texture, Side Texture or Environment Image; black without one), `iChannel1` (a 256 × 256 noise texture), `iChannel2` and `iChannel3` (black) and `iChannelResolution`.
- A face or side shader's picture is used like a texture: it multiplies the colour (keep `FaceColor` white and `T3Metal` 0 to see its colours; `T3Emission` 0.3 to 0.6 makes it glow).
- The environment shader draws the panorama: x once around, y from straight down (0) to straight up (1).
- Give the user the shader as its own code block marked `glsl`, ask them to save it as a `.glsl` file (for example in Documents), and point the node to it with a full path. **Shader Status** on the Textures page shows whether it compiled.
- A slow shader slows every frame; one that takes seconds per frame can make the graphics driver reset. Keep loops short.

## 12. What looks good

**House style:**

- **Still by default.** Textizo3D starts with every row off; add animation only when asked.
- **Fast entrances, a still hold, quick exits.** Reveals take 8 to 20 frames: blur-ins (Blur and Opacity by letters) or sticker-style pops (Size with Out Back or Out Elastic, a little Rotation Z). The text then holds still. No long slides across the frame.
- **Short, big text:** one to four words, filling about half to three quarters of the frame's width.
- **Weight:** heavy fonts (Anton, Archivo Black, Luckiest Guy, Montserrat Black, Poppins Black, Impact) read best in 3D. Give them depth (`ExtrusionDepth` 0.3 to 0.4) and a small bevel (0.02 to 0.04).
- **Camera:** the default three-quarter view, or a low hero angle (`T3CamTilt` -12 to -16, `T3CamFov` 40 to 45, `T3CamDistance` 3 to 3.5).
- **Over footage:** a Shadow Only floor or wall, and Edge Glow or a darker side colour to separate the text from the picture.
- **Moving letters:** `MotionBlur` 1.

**Material recipes** (checked in Textizo3D's renders; values not listed stay at their defaults):

| Look | Values |
|---|---|
| Chrome | `FaceColor` 0.95, 0.95, 0.97; `SideColor` 0.75, 0.77, 0.8; `T3Metal` 1; `T3Roughness` 0.05; `T3Coat` 0; `T3Smudges` 0; `T3EnvIntensity` 1.6; `T3Strips` 1; `T3StripCount` 12; `T3StripWidth` 1.4; `EnvironmentTop` 1, 1, 1; `EnvironmentBottom` 0.01, 0.01, 0.015; `T3KeyIntensity` 0.6; `ExtrusionDepth` 0.3; bevels 0.03 |
| Gold | `FaceColor` 1, 0.86, 0.5; `SideColor` 0.9, 0.62, 0.2; `T3Metal` 1; `T3Roughness` 0.15; `T3Coat` 0; `T3Smudges` 0.1; `T3EnvIntensity` 1.6; `T3Strips` 1; `T3StripCount` 14; `EnvironmentTop` 1, 0.95, 0.85; `EnvironmentBottom` 0.15, 0.1, 0.04; `T3KeyIntensity` 0.8; bevels 0.03 |
| Glossy plastic (candy) | `FaceColor` 1, 0.22, 0.5; `SideColor` 0.75, 0.06, 0.3; `T3Roughness` 0.35; `T3Coat` 1; `T3CoatRough` 0.04; `T3Smudges` 0; `ExtrusionDepth` 0.35; bevels 0.04 |
| Bold red plastic | `FaceColor` 0.95, 0.08, 0.1; `SideColor` 0.55, 0.02, 0.04; `T3Roughness` 0.3; `T3Coat` 1; `T3CoatRough` 0.03; `T3Smudges` 0; `ExtrusionDepth` 0.4; `BevelDepth` 0.035; `BevelWidth` 0.03; `T3FloorMode` 1 |
| Neon | `FaceColor` 0.25, 0.95, 1; `SideColor` 0.04, 0.18, 0.25; `T3Emission` 0.9; `T3Glow` 1.2; `T3GlowSize` 50; `T3GlowThreshold` 0.35; `T3EdgeGlow` 1.2; `EdgeColor` 0.85, 1, 1; `T3KeyIntensity` 0.25; `T3FillIntensity` 0.1; `T3AmbientIntensity` 0; `T3EnvIntensity` 0.3; `T3Strips` 0.2; `T3Smudges` 0 |
| Matte | `FaceColor` 0.95, 0.93, 0.88; `SideColor` 0.55, 0.5, 0.45; `T3Roughness` 0.9; `T3Coat` 0; `T3Smudges` 0; `T3EnvIntensity` 0.3; `T3Strips` 0; `T3FloorMode` 1; `T3ShadowDarkness` 0.5 |
| Worn steel | `FaceColor` 0.7, 0.72, 0.75; `SideColor` 0.45, 0.47, 0.5; `T3Metal` 1; `T3Roughness` 0.35; `T3Bump` 0.6; `T3Scratches` 1; `T3Smudges` 0.4; `T3EnvIntensity` 1.2; `T3Strips` 0.8 |
| Textured | `FaceTexture` a texture (section 11) with `FaceColor` 1, 1, 1; `TexMapping` 0; `T3Roughness` and `T3Metal` to suit the image (metal textures: `T3Metal` 1) |

## 13. Ready looks

Textizo3D's **Look** menu has these looks. On the Edit page, or on a node already in Fusion, the user can pick them from that menu (it keeps the text). In this guide's numbering, start new looks after them.

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

## 14. Control reference

Every input a node can set, with its default. Dropdowns list their numbers. Inputs not listed here are internal: leave them out.

<!-- controls -->
**Text page**

| ID | Control | Kind | Default | Range or choices |
|---|---|---|---|---|
| `Text` | Text | text | "TEXTIZO" | text |
| `Font` | Font Name | string | "Arial Black" | text |
| `Style` | Style Name | string | "Regular" | text |
| `Size` | Size | number | 1 | slider 0 to 5; at least 0 |
| `Tracking` | Tracking | number | 1 | slider 0 to 3; at least 0 |
| `LineSpacing` | Line Spacing | number | 1 | slider 0 to 3; at least 0 |
| `Alignment` | Alignment | choice | 1 | 0 Left, 1 Center, 2 Right |
| `PositionX` | Position and Rotation: Position X | number | 0 | slider -2 to 2 |
| `PositionY` | Position and Rotation: Position Y | number | 0 | slider -2 to 2 |
| `PositionZ` | Position and Rotation: Position Z | number | 0 | slider -2 to 2 |
| `RotationX` | Position and Rotation: Rotation X | number | 0 | slider -180 to 180 |
| `RotationY` | Position and Rotation: Rotation Y | number | 0 | slider -180 to 180 |
| `RotationZ` | Position and Rotation: Rotation Z | number | 0 | slider -180 to 180 |

**In page**

| ID | Control | Kind | Default | Range or choices |
|---|---|---|---|---|
| `T3InOpacityOn` | Opacity: On | checkbox | 0 | 0 or 1 |
| `T3InOpacityPieces` | Opacity: Animate | choice | 0 | 0 Letters, 1 Words, 2 Lines |
| `T3InOpacityOrder` | Opacity: Order | choice | 0 | 0 to 5: the orders in section 4 |
| `T3InOpacityStart` | Opacity: Start Frame | integer | 0 | slider 0 to 250; at least 0 |
| `T3InOpacityEnd` | Opacity: End Frame | integer | 30 | slider 0 to 250; at least 0 |
| `T3InOpacityStagger` | Opacity: Stagger % | number | 30 | slider 0 to 200; at least 0 |
| `T3InOpacityFrom` | Opacity: Start Value | number | 0 | slider 0 to 1 |
| `T3InOpacityTo` | Opacity: End Value | number | 1 | slider 0 to 1 |
| `T3InOpacityEase` | Opacity: Ease | choice | 2 | 0 to 30: the eases in section 6 |
| `T3InBlurOn` | Blur: On | checkbox | 0 | 0 or 1 |
| `T3InBlurPieces` | Blur: Animate | choice | 0 | 0 Letters, 1 Words, 2 Lines |
| `T3InBlurOrder` | Blur: Order | choice | 0 | 0 to 5: the orders in section 4 |
| `T3InBlurStart` | Blur: Start Frame | integer | 0 | slider 0 to 250; at least 0 |
| `T3InBlurEnd` | Blur: End Frame | integer | 30 | slider 0 to 250; at least 0 |
| `T3InBlurStagger` | Blur: Stagger % | number | 30 | slider 0 to 200; at least 0 |
| `T3InBlurFrom` | Blur: Start Value | number | 0.1 | slider 0 to 0.2 |
| `T3InBlurTo` | Blur: End Value | number | 0 | slider 0 to 0.2 |
| `T3InBlurEase` | Blur: Ease | choice | 5 | 0 to 30: the eases in section 6 |
| `T3InPosOn` | Position: On | checkbox | 0 | 0 or 1 |
| `T3InPosPieces` | Position: Animate | choice | 0 | 0 Letters, 1 Words, 2 Lines |
| `T3InPosOrder` | Position: Order | choice | 0 | 0 to 5: the orders in section 4 |
| `T3InPosStart` | Position: Start Frame | integer | 0 | slider 0 to 250; at least 0 |
| `T3InPosEnd` | Position: End Frame | integer | 30 | slider 0 to 250; at least 0 |
| `T3InPosStagger` | Position: Stagger % | number | 30 | slider 0 to 200; at least 0 |
| `T3InPosFromX` | Position: Start X | number | 0 | slider -2 to 2 |
| `T3InPosFromY` | Position: Start Y | number | -0.6 | slider -2 to 2 |
| `T3InPosFromZ` | Position: Start Z | number | 0 | slider -2 to 2 |
| `T3InPosToX` | Position: End X | number | 0 | slider -2 to 2 |
| `T3InPosToY` | Position: End Y | number | 0 | slider -2 to 2 |
| `T3InPosToZ` | Position: End Z | number | 0 | slider -2 to 2 |
| `T3InPosEase` | Position: Ease | choice | 5 | 0 to 30: the eases in section 6 |
| `T3InSizeOn` | Size: On | checkbox | 0 | 0 or 1 |
| `T3InSizePieces` | Size: Animate | choice | 0 | 0 Letters, 1 Words, 2 Lines |
| `T3InSizeOrder` | Size: Order | choice | 0 | 0 to 5: the orders in section 4 |
| `T3InSizeStart` | Size: Start Frame | integer | 0 | slider 0 to 250; at least 0 |
| `T3InSizeEnd` | Size: End Frame | integer | 30 | slider 0 to 250; at least 0 |
| `T3InSizeStagger` | Size: Stagger % | number | 30 | slider 0 to 200; at least 0 |
| `T3InSizeFrom` | Size: Start Value | number | 0 | slider 0 to 4 |
| `T3InSizeTo` | Size: End Value | number | 1 | slider 0 to 4 |
| `T3InSizeEase` | Size: Ease | choice | 23 | 0 to 30: the eases in section 6 |
| `T3InTrackOn` | Tracking: On | checkbox | 0 | 0 or 1 |
| `T3InTrackPieces` | Tracking: Animate | choice | 0 | 0 Letters, 1 Words, 2 Lines |
| `T3InTrackOrder` | Tracking: Order | choice | 0 | 0 to 5: the orders in section 4 |
| `T3InTrackStart` | Tracking: Start Frame | integer | 0 | slider 0 to 250; at least 0 |
| `T3InTrackEnd` | Tracking: End Frame | integer | 30 | slider 0 to 250; at least 0 |
| `T3InTrackStagger` | Tracking: Stagger % | number | 30 | slider 0 to 200; at least 0 |
| `T3InTrackFrom` | Tracking: Start Value | number | 2 | slider -1 to 3 |
| `T3InTrackTo` | Tracking: End Value | number | 0 | slider -1 to 3 |
| `T3InTrackEase` | Tracking: Ease | choice | 5 | 0 to 30: the eases in section 6 |
| `T3InRotOn` | Rotation: On | checkbox | 0 | 0 or 1 |
| `T3InRotPieces` | Rotation: Animate | choice | 0 | 0 Letters, 1 Words, 2 Lines |
| `T3InRotOrder` | Rotation: Order | choice | 0 | 0 to 5: the orders in section 4 |
| `T3InRotStart` | Rotation: Start Frame | integer | 0 | slider 0 to 250; at least 0 |
| `T3InRotEnd` | Rotation: End Frame | integer | 30 | slider 0 to 250; at least 0 |
| `T3InRotStagger` | Rotation: Stagger % | number | 30 | slider 0 to 200; at least 0 |
| `T3InRotFromX` | Rotation: Start X | number | 90 | slider -360 to 360 |
| `T3InRotFromY` | Rotation: Start Y | number | 0 | slider -360 to 360 |
| `T3InRotFromZ` | Rotation: Start Z | number | 0 | slider -360 to 360 |
| `T3InRotToX` | Rotation: End X | number | 0 | slider -360 to 360 |
| `T3InRotToY` | Rotation: End Y | number | 0 | slider -360 to 360 |
| `T3InRotToZ` | Rotation: End Z | number | 0 | slider -360 to 360 |
| `T3InRotEase` | Rotation: Ease | choice | 23 | 0 to 30: the eases in section 6 |
| `T3InExplodeOn` | Explosion: On | checkbox | 0 | 0 or 1 |
| `T3InExplodePieces` | Explosion: Animate | choice | 0 | 0 Letters, 1 Words, 2 Lines |
| `T3InExplodeOrder` | Explosion: Order | choice | 0 | 0 to 5: the orders in section 4 |
| `T3InExplodeStart` | Explosion: Start Frame | integer | 0 | slider 0 to 250; at least 0 |
| `T3InExplodeEnd` | Explosion: End Frame | integer | 30 | slider 0 to 250; at least 0 |
| `T3InExplodeStagger` | Explosion: Stagger % | number | 30 | slider 0 to 200; at least 0 |
| `T3InExplodeFrom` | Explosion: Start Value | number | 1.5 | slider 0 to 3 |
| `T3InExplodeTo` | Explosion: End Value | number | 0 | slider 0 to 3 |
| `T3InExplodeDamping` | Explosion: Damping | number | 0 | slider 0 to 8; at least 0 |
| `T3InExplodeVariance` | Explosion: Variance | number | 0.35 | 0 to 1 |
| `T3InExplodeSpinX` | Explosion: Spin X | number | 180 | slider 0 to 720 |
| `T3InExplodeSpinY` | Explosion: Spin Y | number | 180 | slider 0 to 720 |
| `T3InExplodeSpinZ` | Explosion: Spin Z | number | 240 | slider 0 to 1440 |
| `T3InExplodePreRoll` | Explosion: Pre-Roll | integer | 0 | slider 0 to 250; at least 0 |
| `T3InExplodeReverse` | Explosion: Reverse | checkbox | 0 | 0 or 1 |
| `T3InExplodeEase` | Explosion: Ease | choice | 5 | 0 to 30: the eases in section 6 |

**Out page**

| ID | Control | Kind | Default | Range or choices |
|---|---|---|---|---|
| `T3OutOpacityOn` | Opacity: On | checkbox | 0 | 0 or 1 |
| `T3OutOpacityPieces` | Opacity: Animate | choice | 0 | 0 Letters, 1 Words, 2 Lines |
| `T3OutOpacityOrder` | Opacity: Order | choice | 0 | 0 to 5: the orders in section 4 |
| `T3OutOpacityStart` | Opacity: Start Frame | integer | 90 | slider 0 to 250; at least 0 |
| `T3OutOpacityEnd` | Opacity: End Frame | integer | 115 | slider 0 to 250; at least 0 |
| `T3OutOpacityStagger` | Opacity: Stagger % | number | 30 | slider 0 to 200; at least 0 |
| `T3OutOpacityTo` | Opacity: End Value | number | 0 | slider 0 to 1 |
| `T3OutOpacityEase` | Opacity: Ease | choice | 1 | 0 to 30: the eases in section 6 |
| `T3OutBlurOn` | Blur: On | checkbox | 0 | 0 or 1 |
| `T3OutBlurPieces` | Blur: Animate | choice | 0 | 0 Letters, 1 Words, 2 Lines |
| `T3OutBlurOrder` | Blur: Order | choice | 0 | 0 to 5: the orders in section 4 |
| `T3OutBlurStart` | Blur: Start Frame | integer | 90 | slider 0 to 250; at least 0 |
| `T3OutBlurEnd` | Blur: End Frame | integer | 115 | slider 0 to 250; at least 0 |
| `T3OutBlurStagger` | Blur: Stagger % | number | 30 | slider 0 to 200; at least 0 |
| `T3OutBlurTo` | Blur: End Value | number | 0.1 | slider 0 to 0.2 |
| `T3OutBlurEase` | Blur: Ease | choice | 1 | 0 to 30: the eases in section 6 |
| `T3OutPosOn` | Position: On | checkbox | 0 | 0 or 1 |
| `T3OutPosPieces` | Position: Animate | choice | 0 | 0 Letters, 1 Words, 2 Lines |
| `T3OutPosOrder` | Position: Order | choice | 0 | 0 to 5: the orders in section 4 |
| `T3OutPosStart` | Position: Start Frame | integer | 90 | slider 0 to 250; at least 0 |
| `T3OutPosEnd` | Position: End Frame | integer | 115 | slider 0 to 250; at least 0 |
| `T3OutPosStagger` | Position: Stagger % | number | 30 | slider 0 to 200; at least 0 |
| `T3OutPosToX` | Position: End X | number | 0 | slider -2 to 2 |
| `T3OutPosToY` | Position: End Y | number | 0.6 | slider -2 to 2 |
| `T3OutPosToZ` | Position: End Z | number | 0 | slider -2 to 2 |
| `T3OutPosEase` | Position: Ease | choice | 4 | 0 to 30: the eases in section 6 |
| `T3OutSizeOn` | Size: On | checkbox | 0 | 0 or 1 |
| `T3OutSizePieces` | Size: Animate | choice | 0 | 0 Letters, 1 Words, 2 Lines |
| `T3OutSizeOrder` | Size: Order | choice | 0 | 0 to 5: the orders in section 4 |
| `T3OutSizeStart` | Size: Start Frame | integer | 90 | slider 0 to 250; at least 0 |
| `T3OutSizeEnd` | Size: End Frame | integer | 115 | slider 0 to 250; at least 0 |
| `T3OutSizeStagger` | Size: Stagger % | number | 30 | slider 0 to 200; at least 0 |
| `T3OutSizeTo` | Size: End Value | number | 0 | slider 0 to 4 |
| `T3OutSizeEase` | Size: Ease | choice | 22 | 0 to 30: the eases in section 6 |
| `T3OutTrackOn` | Tracking: On | checkbox | 0 | 0 or 1 |
| `T3OutTrackPieces` | Tracking: Animate | choice | 0 | 0 Letters, 1 Words, 2 Lines |
| `T3OutTrackOrder` | Tracking: Order | choice | 0 | 0 to 5: the orders in section 4 |
| `T3OutTrackStart` | Tracking: Start Frame | integer | 90 | slider 0 to 250; at least 0 |
| `T3OutTrackEnd` | Tracking: End Frame | integer | 115 | slider 0 to 250; at least 0 |
| `T3OutTrackStagger` | Tracking: Stagger % | number | 30 | slider 0 to 200; at least 0 |
| `T3OutTrackTo` | Tracking: End Value | number | 2 | slider -1 to 3 |
| `T3OutTrackEase` | Tracking: Ease | choice | 4 | 0 to 30: the eases in section 6 |
| `T3OutRotOn` | Rotation: On | checkbox | 0 | 0 or 1 |
| `T3OutRotPieces` | Rotation: Animate | choice | 0 | 0 Letters, 1 Words, 2 Lines |
| `T3OutRotOrder` | Rotation: Order | choice | 0 | 0 to 5: the orders in section 4 |
| `T3OutRotStart` | Rotation: Start Frame | integer | 90 | slider 0 to 250; at least 0 |
| `T3OutRotEnd` | Rotation: End Frame | integer | 115 | slider 0 to 250; at least 0 |
| `T3OutRotStagger` | Rotation: Stagger % | number | 30 | slider 0 to 200; at least 0 |
| `T3OutRotToX` | Rotation: End X | number | -90 | slider -360 to 360 |
| `T3OutRotToY` | Rotation: End Y | number | 0 | slider -360 to 360 |
| `T3OutRotToZ` | Rotation: End Z | number | 0 | slider -360 to 360 |
| `T3OutRotEase` | Rotation: Ease | choice | 22 | 0 to 30: the eases in section 6 |
| `T3OutExplodeOn` | Explosion: On | checkbox | 0 | 0 or 1 |
| `T3OutExplodePieces` | Explosion: Animate | choice | 0 | 0 Letters, 1 Words, 2 Lines |
| `T3OutExplodeOrder` | Explosion: Order | choice | 0 | 0 to 5: the orders in section 4 |
| `T3OutExplodeStart` | Explosion: Start Frame | integer | 90 | slider 0 to 250; at least 0 |
| `T3OutExplodeEnd` | Explosion: End Frame | integer | 115 | slider 0 to 250; at least 0 |
| `T3OutExplodeStagger` | Explosion: Stagger % | number | 30 | slider 0 to 200; at least 0 |
| `T3OutExplodeTo` | Explosion: End Value | number | 1.5 | slider 0 to 3 |
| `T3OutExplodeDamping` | Explosion: Damping | number | 0 | slider 0 to 8; at least 0 |
| `T3OutExplodeVariance` | Explosion: Variance | number | 0.35 | 0 to 1 |
| `T3OutExplodeSpinX` | Explosion: Spin X | number | 180 | slider 0 to 720 |
| `T3OutExplodeSpinY` | Explosion: Spin Y | number | 180 | slider 0 to 720 |
| `T3OutExplodeSpinZ` | Explosion: Spin Z | number | 240 | slider 0 to 1440 |
| `T3OutExplodePreRoll` | Explosion: Pre-Roll | integer | 0 | slider 0 to 250; at least 0 |
| `T3OutExplodeReverse` | Explosion: Reverse | checkbox | 0 | 0 or 1 |
| `T3OutExplodeEase` | Explosion: Ease | choice | 4 | 0 to 30: the eases in section 6 |

**Shape page**

| ID | Control | Kind | Default | Range or choices |
|---|---|---|---|---|
| `ExtrusionDepth` | Extrusion Depth | number | 0.25 | slider 0 to 1; at least 0 |
| `BevelDepth` | Bevel Depth | number | 0.015 | slider 0 to 0.1; at least 0 |
| `BevelWidth` | Bevel Width | number | 0.015 | slider 0 to 0.1; at least 0 |
| `FrontBevel` | Bevel Details: Front | checkbox | 1 | 0 or 1 |
| `BackBevel` | Bevel Details: Back | checkbox | 1 | 0 or 1 |
| `SmoothingAngle` | Bevel Details: Smoothing Angle | number | 30 | slider 0 to 90; allowed 0 to 180 |

**Material page**

| ID | Control | Kind | Default | Range or choices |
|---|---|---|---|---|
| `FaceColor` (`FaceColorRed`, `FaceColorGreen`, `FaceColorBlue`) | Color: Face Color | color | [1, 1, 1] | red, green, blue from 0 to 1 |
| `SideColor` (`SideColorRed`, `SideColorGreen`, `SideColorBlue`) | Color: Side Color | color | [0.45, 0.5, 0.6] | red, green, blue from 0 to 1 |
| `T3Roughness` | Surface: Roughness | number | 0.35 | 0 to 1 |
| `T3Metal` | Surface: Metalness | number | 0 | 0 to 1 |
| `T3Coat` | Surface: Clear Coat | number | 0.4 | 0 to 1 |
| `T3Emission` | Surface: Emission | number | 0 | slider 0 to 1; at least 0 |
| `T3CoatRough` | Surface Details: Coat Roughness | number | 0.06 | 0 to 1 |
| `T3Specular` | Surface Details: Reflectivity | number | 1 | slider 0 to 1; at least 0 |
| `T3Bump` | Wear: Face Bump | number | 0 | slider 0 to 1; allowed 0 to 4 |
| `T3Scratches` | Wear: Scratches | number | 0 | 0 to 1 |
| `T3Smudges` | Wear: Smudges | number | 0.15 | slider 0 to 0.6; allowed 0 to 1 |
| `T3BumpStyle` | Wear Details: Bump Style | choice | 0 | 0 Hammered, 1 Smooth |
| `T3BumpSize` | Wear Details: Bump Size | number | 1.5 | slider 0.2 to 4; at least 0.05 |
| `T3BumpDetail` | Wear Details: Bump Detail | integer | 1 | slider 1 to 8; at least 1 |
| `T3SideBump` | Wear Details: Side Bump | number | 0 | slider 0 to 1; allowed 0 to 4 |
| `T3ScratchCount` | Wear Details: Scratch Count | number | 14 | slider 2 to 40; at least 0.5 |
| `T3ScratchLength` | Wear Details: Scratch Length | number | 1 | slider 0.2 to 3; at least 0.05 |
| `T3ScratchWidth` | Wear Details: Scratch Width | number | 1 | slider 0.3 to 3; at least 0.05 |
| `T3ScratchAngle` | Wear Details: Scratch Angle | number | 25 | slider -180 to 180 |
| `T3ScratchSeed` | Wear Details: Scratch Seed | number | 0 | slider 0 to 100 |
| `T3SmudgeSize` | Wear Details: Smudge Size | number | 1 | slider 0.2 to 4; at least 0.05 |
| `T3SmudgeSeed` | Wear Details: Smudge Seed | number | 0 | slider 0 to 100 |
| `T3EdgeGlow` | Glow: Edge Glow | number | 0 | slider 0 to 3; at least 0 |
| `T3Glow` | Glow | number | 0 | slider 0 to 3; at least 0 |
| `EdgeColor` (`EdgeColorRed`, `EdgeColorGreen`, `EdgeColorBlue`) | Glow Details: Edge Color | color | [1, 1, 1] | red, green, blue from 0 to 1 |
| `T3EdgeWidth` | Glow Details: Edge Width | number | 2 | slider 0.5 to 10; at least 0 |
| `T3EdgeSoft` | Glow Details: Edge Softness | number | 6 | slider 0 to 30; at least 0 |
| `T3GlowSize` | Glow Details: Glow Size | number | 20 | slider 1 to 100; at least 0 |
| `T3GlowThreshold` | Glow Details: Glow Threshold | number | 0.7 | slider 0 to 1; at least 0 |
| `T3FxBeyond` | Effects: Beyond the Letters | checkbox | 1 | 0 or 1 |
| `T3FireOn` | Effects: Fire | checkbox | 0 | 0 or 1 |
| `T3FireFlames` | Effects: Flames | number | 1 | slider 0 to 2; at least 0 |
| `T3FireHeight` | Effects: Flame Height | number | 1 | slider 0 to 3; at least 0 |
| `T3FireEmbers` | Effects: Embers | number | 1 | slider 0 to 3; at least 0 |
| `T3FireSpeed` | Effects: Fire Speed | number | 1 | slider 0 to 3; at least 0 |
| `FireColor` (`FireColorRed`, `FireColorGreen`, `FireColorBlue`) | Effects: Fire Color | color | [1, 0.42, 0.06] | red, green, blue from 0 to 1 |
| `T3FrostOn` | Effects: Frost | checkbox | 0 | 0 or 1 |
| `T3FrostMist` | Effects: Mist | number | 1 | slider 0 to 2; at least 0 |
| `T3FrostHeight` | Effects: Mist Reach | number | 1 | slider 0 to 3; at least 0 |
| `T3FrostSnow` | Effects: Snow | number | 1 | slider 0 to 3; at least 0 |
| `T3FrostSpeed` | Effects: Frost Speed | number | 1 | slider 0 to 3; at least 0 |
| `FrostColor` (`FrostColorRed`, `FrostColorGreen`, `FrostColorBlue`) | Effects: Frost Color | color | [0.75, 0.92, 1] | red, green, blue from 0 to 1 |
| `T3SparkleOn` | Effects: Sparkles | checkbox | 0 | 0 or 1 |
| `T3SparkleAmount` | Effects: Sparkle Amount | number | 1 | slider 0 to 3; at least 0 |
| `T3SparkleSize` | Effects: Sparkle Size | number | 1 | slider 0 to 3; at least 0 |
| `T3SparkleSpeed` | Effects: Twinkle Speed | number | 1 | slider 0 to 3; at least 0 |
| `SparkleColor` (`SparkleColorRed`, `SparkleColorGreen`, `SparkleColorBlue`) | Effects: Sparkle Color | color | [1, 1, 1] | red, green, blue from 0 to 1 |

**Camera page**

| ID | Control | Kind | Default | Range or choices |
|---|---|---|---|---|
| `T3CamDistance` | Camera: Distance | number | 4.8 | slider 1 to 20; at least 0.1 |
| `T3CamFov` | Camera: Field of View | number | 30 | slider 5 to 100; allowed 1 to 170 |
| `T3CamOrbit` | Camera: Orbit | number | -18 | slider -180 to 180 |
| `T3CamTilt` | Camera: Tilt | number | 10 | -89 to 89 |
| `T3CamTargetY` | Camera Details: Look At Height | number | 0 | slider -2 to 2 |
| `T3CamDrift` | Camera Details: Orbit Drift (over clip) | number | 0 | slider -90 to 90 |
| `T3CamPush` | Camera Details: Push In % (over clip) | number | 0 | slider -50 to 50; allowed -90 to 90 |
| `MotionBlur` | Render Quality: Motion Blur | checkbox | 0 | 0 or 1 |
| `BlurQuality` | Render Quality: Blur Quality | integer | 4 | slider 1 to 16; allowed 1 to 64 |
| `ShutterAngle` | Render Quality: Shutter Angle | number | 180 | slider 0 to 360; allowed 0 to 720 |
| `EdgeSmoothing` | Render Quality: Edge Smoothing | integer | 2 | slider 1 to 4; allowed 1 to 8 |
| `T3HoldStill` | Render Quality: Reuse Still Frames | checkbox | 1 | 0 or 1 |

**Light page**

| ID | Control | Kind | Default | Range or choices |
|---|---|---|---|---|
| `T3KeyIntensity` | Key Light | number | 0.9 | slider 0 to 2; at least 0 |
| `KeyColor` (`KeyColorRed`, `KeyColorGreen`, `KeyColorBlue`) | Key Light: Key Color | color | [1, 1, 1] | red, green, blue from 0 to 1 |
| `T3KeyAngle` | Key Light: Key Angle | number | -35 | slider -180 to 180 |
| `T3KeyHeight` | Key Light: Key Height | number | 40 | slider -10 to 90; allowed -89 to 89 |
| `T3KeySpread` | Key Details: Key Spread | number | 70 | slider 10 to 170; allowed 1 to 179 |
| `T3KeyFalloff` | Key Details: Key Edge Softness | number | 20 | slider 0 to 90; at least 0 |
| `T3Shadows` | Shadows | checkbox | 1 | 0 or 1 |
| `T3FloorMode` | Shadows: Floor | choice | 0 | 0 Off, 1 Shadow Only, 2 Visible |
| `T3WallMode` | Shadows: Wall | choice | 0 | 0 Off, 1 Shadow Only, 2 Visible |
| `T3ShadowDarkness` | Shadows: Shadow Darkness | number | 0.6 | 0 to 1 |
| `T3ShadowSoftness` | Shadows: Shadow Softness | number | 0.015 | slider 0 to 0.05; at least 0 |
| `T3FloorGap` | Floor and Wall Details: Floor Gap | number | 0.15 | slider -1 to 1 |
| `FloorColor` (`FloorColorRed`, `FloorColorGreen`, `FloorColorBlue`) | Floor and Wall Details: Floor Color | color | [0.5, 0.5, 0.52] | red, green, blue from 0 to 1 |
| `T3WallDistance` | Floor and Wall Details: Wall Distance | number | 0.4 | slider 0 to 3; at least 0 |
| `WallColor` (`WallColorRed`, `WallColorGreen`, `WallColorBlue`) | Floor and Wall Details: Wall Color | color | [0.5, 0.5, 0.52] | red, green, blue from 0 to 1 |
| `T3FillIntensity` | Fill Lights: Fill Light | number | 0.25 | slider 0 to 2; at least 0 |
| `T3AmbientIntensity` | Fill Lights: Ambient Light | number | 0.2 | slider 0 to 2; at least 0 |
| `T3UnderIntensity` | Fill Lights: Under Light | number | 0 | slider 0 to 2; at least 0 |
| `FillColor` (`FillColorRed`, `FillColorGreen`, `FillColorBlue`) | Fill Details: Fill Color | color | [1, 1, 1] | red, green, blue from 0 to 1 |
| `T3FillAngle` | Fill Details: Fill Angle | number | 28 | slider -180 to 180 |
| `UnderColor` (`UnderColorRed`, `UnderColorGreen`, `UnderColorBlue`) | Fill Details: Under Color | color | [1, 1, 1] | red, green, blue from 0 to 1 |
| `T3EnvIntensity` | Reflections | number | 1 | slider 0 to 3; at least 0 |
| `T3Strips` | Reflections: Light Strips | number | 0.6 | slider 0 to 1; at least 0 |
| `EnvironmentTop` (`EnvironmentTopRed`, `EnvironmentTopGreen`, `EnvironmentTopBlue`) | Environment Details: Environment Top | color | [0.7, 0.75, 0.8] | red, green, blue from 0 to 1 |
| `EnvironmentBottom` (`EnvironmentBottomRed`, `EnvironmentBottomGreen`, `EnvironmentBottomBlue`) | Environment Details: Environment Bottom | color | [0.04, 0.04, 0.05] | red, green, blue from 0 to 1 |
| `T3StripCount` | Environment Details: Strip Count | number | 20 | slider 2 to 60; at least 1 |
| `T3StripWidth` | Environment Details: Strip Width | number | 1 | slider 0.3 to 3; at least 0.05 |
| `T3EnvRotation` | Environment Details: Environment Rotation | number | 0 | slider -180 to 180 |

**Textures page**

| ID | Control | Kind | Default | Range or choices |
|---|---|---|---|---|
| `FaceTexture` | Face Texture | file | "" | a file path, or `textures/<file>` for a texture Textizo3D carries |
| `SideTexture` | Side Texture | file | "" | a file path, or `textures/<file>` for a texture Textizo3D carries |
| `TexMapping` | Texture Mapping | choice | 0 | 0 Whole Text, 1 Per Word, 2 Per Letter |
| `TexScale` | Texture Scale | number | 1 | slider 0 to 4; at least 0 |
| `FaceShader` | Face Shader | file | "" | a file path, or `textures/<file>` for a texture Textizo3D carries |
| `SideShader` | Side Shader | file | "" | a file path, or `textures/<file>` for a texture Textizo3D carries |
| `EnvImage` | Environment Image | file | "" | a file path, or `textures/<file>` for a texture Textizo3D carries |
| `EnvShader` | Environment Shader | file | "" | a file path, or `textures/<file>` for a texture Textizo3D carries |
| `ShaderSpeed` | Shader Speed | number | 1 | slider 0 to 3; at least 0 |
<!-- /controls -->

## 15. Example 1: a ready look

The first ready look, `Textizo3D-01A`: big green glossy money digits with dents, scratches, an edge glow and a soft glow, seen from below, with its shadow on an invisible wall. Pasted as a new node, everything not listed is at its default.

<!-- example: Textizo3D-01A -->
```lua
{
	Tools = ordered() {
		Textizo3D1 = ofx.com.clipizo.textizo3dfx {
			Inputs = {
				Text = Input { Value = "$1,000", },
				Font = Input { Value = "Inter", },
				Style = Input { Value = "Black", },
				Tracking = Input { Value = 0.86, },
				PositionY = Input { Value = 0.145, },
				RotationX = Input { Value = -7.8, },
				RotationY = Input { Value = -7.8, },
				RotationZ = Input { Value = -2.6, },
				ExtrusionDepth = Input { Value = 0.34, },
				BevelDepth = Input { Value = 0.03, },
				BevelWidth = Input { Value = 0.03, },
				SmoothingAngle = Input { Value = 60, },
				FaceColorRed = Input { Value = 0.06, },
				FaceColorGreen = Input { Value = 0.55, },
				FaceColorBlue = Input { Value = 0.07, },
				SideColorRed = Input { Value = 0.05, },
				SideColorGreen = Input { Value = 0.5, },
				SideColorBlue = Input { Value = 0.07, },
				T3Roughness = Input { Value = 0.25, },
				T3Coat = Input { Value = 0.8, },
				T3Emission = Input { Value = 0.32, },
				T3Bump = Input { Value = 0.6, },
				T3Scratches = Input { Value = 1, },
				T3Smudges = Input { Value = 0.45, },
				T3BumpSize = Input { Value = 1, },
				T3SmudgeSeed = Input { Value = 1, },
				T3EdgeGlow = Input { Value = 1.2, },
				T3Glow = Input { Value = 0.7, },
				EdgeColorRed = Input { Value = 0.75, },
				EdgeColorGreen = Input { Value = 1, },
				EdgeColorBlue = Input { Value = 0.75, },
				T3EdgeWidth = Input { Value = 0.45, },
				T3EdgeSoft = Input { Value = 4, },
				T3GlowSize = Input { Value = 45, },
				T3GlowThreshold = Input { Value = 0.55, },
				T3CamDistance = Input { Value = 3.24, },
				T3CamFov = Input { Value = 45, },
				T3CamOrbit = Input { Value = -10, },
				T3CamTilt = Input { Value = -16, },
				T3CamTargetY = Input { Value = 0.12, },
				T3KeyAngle = Input { Value = -20, },
				T3KeyHeight = Input { Value = 25, },
				T3WallMode = Input { Value = 1, },
				T3ShadowDarkness = Input { Value = 0.5, },
				T3FillIntensity = Input { Value = 0.15, },
				T3AmbientIntensity = Input { Value = 0, },
				T3UnderIntensity = Input { Value = 0.7, },
				T3FillAngle = Input { Value = 16, },
				T3Strips = Input { Value = 1, },
				EnvironmentTopRed = Input { Value = 0.25, },
				EnvironmentTopGreen = Input { Value = 0.6, },
				EnvironmentTopBlue = Input { Value = 0.5, },
				EnvironmentBottomRed = Input { Value = 0.02, },
				EnvironmentBottomGreen = Input { Value = 0.12, },
				EnvironmentBottomBlue = Input { Value = 0.08, },
			},
			ViewInfo = OperatorInfo { Pos = { 0, 0 } },
		},
	},
	ActiveTool = "Textizo3D1"
}
```
<!-- /example: Textizo3D-01A -->

## 16. Example 2: a variation with animation

`Textizo3D-01B`: the same worn look in gold metal on "LEVEL UP", set in Inter Black (a font Textizo3D carries). The letters blur, fade and pop in from left to right (frames 0 to 18: each letter about 6 frames, starting 2 frames after the one before), hold, and blur out by words at the end of a 5-second clip at 24 fps (frames 104 to 116), with motion blur on.

<!-- example: Textizo3D-01B -->
```lua
{
	Tools = ordered() {
		Textizo3D1 = ofx.com.clipizo.textizo3dfx {
			Inputs = {
				Text = Input { Value = "LEVEL UP", },
				Font = Input { Value = "Inter", },
				Style = Input { Value = "Black", },
				Tracking = Input { Value = 0.86, },
				PositionY = Input { Value = 0.145, },
				RotationX = Input { Value = -7.8, },
				RotationY = Input { Value = -7.8, },
				RotationZ = Input { Value = -2.6, },
				T3InOpacityOn = Input { Value = 1, },
				T3InOpacityEnd = Input { Value = 17, },
				T3InOpacityStagger = Input { Value = 40, },
				T3InBlurOn = Input { Value = 1, },
				T3InBlurEnd = Input { Value = 18, },
				T3InBlurStagger = Input { Value = 33.3, },
				T3InSizeOn = Input { Value = 1, },
				T3InSizeEnd = Input { Value = 18, },
				T3InSizeStagger = Input { Value = 33.3, },
				T3InSizeFrom = Input { Value = 0.6, },
				T3OutOpacityOn = Input { Value = 1, },
				T3OutOpacityPieces = Input { Value = 1, },
				T3OutOpacityStart = Input { Value = 104, },
				T3OutOpacityEnd = Input { Value = 116, },
				T3OutOpacityStagger = Input { Value = 0, },
				T3OutOpacityEase = Input { Value = 4, },
				T3OutBlurOn = Input { Value = 1, },
				T3OutBlurPieces = Input { Value = 1, },
				T3OutBlurStart = Input { Value = 104, },
				T3OutBlurEnd = Input { Value = 116, },
				T3OutBlurStagger = Input { Value = 0, },
				T3OutBlurEase = Input { Value = 4, },
				ExtrusionDepth = Input { Value = 0.34, },
				BevelDepth = Input { Value = 0.03, },
				BevelWidth = Input { Value = 0.03, },
				SmoothingAngle = Input { Value = 60, },
				FaceColorRed = Input { Value = 1, },
				FaceColorGreen = Input { Value = 0.7843, },
				FaceColorBlue = Input { Value = 0.2392, },
				SideColorRed = Input { Value = 0.5412, },
				SideColorGreen = Input { Value = 0.3529, },
				SideColorBlue = Input { Value = 0.0706, },
				T3Roughness = Input { Value = 0.22, },
				T3Metal = Input { Value = 1, },
				T3Coat = Input { Value = 0.8, },
				T3Bump = Input { Value = 0.6, },
				T3Scratches = Input { Value = 1, },
				T3Smudges = Input { Value = 0.45, },
				T3BumpSize = Input { Value = 1, },
				T3SmudgeSeed = Input { Value = 1, },
				T3EdgeGlow = Input { Value = 1.2, },
				T3Glow = Input { Value = 0.7, },
				EdgeColorRed = Input { Value = 1, },
				EdgeColorGreen = Input { Value = 0.9137, },
				EdgeColorBlue = Input { Value = 0.6588, },
				T3EdgeWidth = Input { Value = 0.45, },
				T3EdgeSoft = Input { Value = 4, },
				T3GlowSize = Input { Value = 45, },
				T3GlowThreshold = Input { Value = 0.55, },
				T3CamDistance = Input { Value = 3.24, },
				T3CamFov = Input { Value = 45, },
				T3CamOrbit = Input { Value = -10, },
				T3CamTilt = Input { Value = -16, },
				T3CamTargetY = Input { Value = 0.12, },
				MotionBlur = Input { Value = 1, },
				T3KeyAngle = Input { Value = -20, },
				T3KeyHeight = Input { Value = 25, },
				T3WallMode = Input { Value = 1, },
				T3ShadowDarkness = Input { Value = 0.5, },
				T3FillIntensity = Input { Value = 0.15, },
				T3AmbientIntensity = Input { Value = 0, },
				T3UnderIntensity = Input { Value = 0.7, },
				T3FillAngle = Input { Value = 16, },
				T3Strips = Input { Value = 1, },
				EnvironmentTopRed = Input { Value = 1, },
				EnvironmentTopGreen = Input { Value = 0.8863, },
				EnvironmentTopBlue = Input { Value = 0.6275, },
				EnvironmentBottomRed = Input { Value = 0.1647, },
				EnvironmentBottomGreen = Input { Value = 0.102, },
				EnvironmentBottomBlue = Input { Value = 0.0314, },
			},
			ViewInfo = OperatorInfo { Pos = { 0, 0 } },
		},
	},
	ActiveTool = "Textizo3D1"
}
```
<!-- /example: Textizo3D-01B -->

## 17. Using a preset in Resolve

- **As a new node:** on the Fusion page, click an empty spot in the Nodes area and paste the code (Ctrl+V, Mac: Cmd+V), or drag a `.setting` file onto the Nodes area.
- **Connect** the node to MediaOut1, or through a Merge over footage (Quick start, step 4). A clip connected to the node's own input becomes its background: the text draws over it.
- **On the Edit page,** put a Fusion Composition on the timeline (Effects > Toolbox > Effects > Fusion Composition), open it on the Fusion page, paste the node and connect it to MediaOut1. Or open the Fusion page on any clip and Merge the text over it.
- **On an existing Textizo3D node:** right-click the node and choose **Settings > Load…**, then pick the `.setting` file. Presets in Resolve's Settings folder are listed in that menu:
  - Windows: `%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Settings`
  - Mac: `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Settings`
  - Linux: `~/.local/share/DaVinciResolve/Fusion/Settings`
- **Your own text:** type it in the Inspector (Text page). The animation follows any length of text.
- **Play** the clip: an entrance's first frames are empty on purpose.

## 18. Troubleshooting

| Problem | Fix |
|---|---|
| Pasting does nothing | Copy the whole block, from the first `{` to the last `}`, and click an empty spot in the Nodes area before pasting. |
| Nothing appears, or Fusion reports an unknown tool | Textizo3D isn't installed, or Resolve wasn't restarted after installing it. |
| The text replaced my video | The node was pasted while another node was selected, so Fusion wired it in. Connect it through a Merge (Quick start, step 4), or connect the clip to the node's own input. |
| The text shows "TEXTIZO" | `Text` wasn't written. |
| The wrong font | The font or style name isn't installed: use a font from section 3, or install it. |
| Letters are cut off at the frame's edge | Lower `Size`, use a narrower font or two lines (section 3), or raise `T3CamDistance`. |
| Nothing moves | The rows' `...On` inputs are 0, or their frames are outside the clip. |
| The first frames are empty | The entrance starts there. Play the clip, or raise its rows' `Start`. |
| The text disappears early | An Out row's `Start` is too early for the clip: move the Out rows' frames to the clip's last second. |
| A texture or shader doesn't show | The path is wrong or the file isn't on this computer. Check the path; see Shader Status on the Textures page. |
| The text looks dark | Metal reflects its environment: raise `T3EnvIntensity` and `T3Strips`, lighten `EnvironmentTop`, or lower `T3Metal`. |
| The node's Inspector has a Page menu instead of tabs | Normal for a pasted node: pick a page from the menu. Nodes built by the kit's tool, or added with Add Tool, show tabs. |
| A new preset is not in the Settings menu | Use Settings > Load… and pick the file, or restart Resolve. |

## 19. Limits

- One node draws one text block (up to a few lines). For several titles, paste several nodes.
- No keyframes: a node from this guide animates with its rows. The user can keyframe any control in Resolve afterwards.
- Letters are drawn one by one, left to right (section 3).
- Textures, environment images and shaders are files: the user's own must exist on the computer that renders. Textures Textizo3D carries (`textures/...`) are always there.
- The `Look` menu, `FontMenu` and `StyleMenu` are never written (section 2).
- There is no colour management: colours are drawn as written, lit, over a transparent background.
