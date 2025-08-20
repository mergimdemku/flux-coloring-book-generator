# Coloring Book Generator App -- Concept & Development Guide

## 1. Product Shape (What the App Does)

-   **Wizard flow:**
    1.  Enter title + age range (e.g., 3--6).
    2.  Pick a theme/story (or auto-generate one).
    3.  Choose page count (e.g., 24 pages: 1 cover, 20 scenes, 2
        activity pages, 1 back cover).
    4.  Generate scenes → preview → regenerate individual pages → lock
        when happy.
    5.  Export: **A4, 300 DPI**, PDF (optionally PDF/X-ready), plus
        PNGs.
-   **Consistency controls:** same main character through all pages
    (dog, collar, bowl, city park...).
-   **Line-art only:** Outputs should be **black outlines on white**, no
    shading or color, thick enough for crayons.

------------------------------------------------------------------------

## 2. Tech Stack Ideas (Desktop)

-   **Python + Qt (PySide6/PyQt)**: native desktop, easy packaging,
    strong PDF libs (ReportLab, Qt PDF).
-   **Tauri/Electron + Python backend**: slick UI with web tech; Python
    handles generation.
-   **.NET (WPF/MAUI) + Python worker**: if you prefer C#/Windows.

**Fastest path:** **PySide6 UI + Python worker (FLUX + ReportLab for
PDFs).**

------------------------------------------------------------------------

## 3. Image Generation with FLUX (Coloring Pages)

### Prompt Template

> "(children's coloring page), **bold clean black outlines**,
> high-contrast line art, **no shading**, no gray, white background,
> simple shapes, minimal detail, subject: {scene}, style: **printable
> vector-like linework**, center composition, kid-friendly"

### Negative Prompt

> "color, grayscale shading, gradients, text, watermarks, signature,
> background clutter, tiny details, crosshatching"

### A4 Framing

-   Generate at **2480×3508 px** (A4 at 300 DPI).
-   If VRAM is tight: generate smaller → upscale with line-preserving
    method.

### Post-Processing

-   **Threshold → thicken lines → clean white background**
    -   OpenCV: adaptive threshold, morphology (dilate 1 px), remove
        specks, ensure pure #000000 lines and pure #FFFFFF background.
-   **Vectorization**: Potrace → SVG → sharp prints.

### Character Consistency

-   Use a **character card** repeated in all prompts:\
    \> "dog named Bibo: small, floppy ears, round nose, striped collar
    with bone tag, friendly, curious, same style each page"

-   Option: fix **seed** for character + vary scene description.

------------------------------------------------------------------------

## 4. Pipeline Architecture

1.  **Story engine** → Theme → JSON storyboard.
2.  **Prompt builder** → Base style + character card + scene
    description + negative prompt.
3.  **FLUX generation** → PNGs → post-process cleanup.
4.  **Quality checks** → heuristics for % black, line thickness, no
    color.
5.  **PDF composer** → add margins, cover, title page, credits.
6.  **Packaging** → `/Books/{slug}/pages/*.png`,
    `/Books/{slug}/book.pdf`, `/Books/{slug}/meta.json`.

------------------------------------------------------------------------

## 5. PDF & Export Details

-   **Size:** A4 (210×297 mm → 2480×3508 px @ 300 DPI).
-   **Margins:** 10--15 mm safe zone.
-   **Cover:** Keep simple, with large title text.
-   **Metadata:** PDF Title, Author, Keywords.
-   **Print services:** Make both A4 and US Letter editions for Amazon
    KDP & EU print.

------------------------------------------------------------------------

## 6. Business & Content Tips

-   **Series strategy:** Same character, multiple adventures.
-   **Age-fit:** Younger → larger shapes; older → more details.
-   **Activities:** Add mazes, tracing, counting games (auto-generated).
-   **Educational angle:** Light tasks: "count 3 bones".
-   **Localization:** Translate captions → multiple editions.
-   **Branding:** Footer: "3D Gravity Kids · Kopshti Magjik" + QR code.

------------------------------------------------------------------------

## 7. Example Storyboard: *"Bibo Searches for Food"*

1.  Bibo wakes up---empty bowl.\
2.  Sniffs yard.\
3.  Finds toy bone.\
4.  Asks bird.\
5.  Checks mailbox.\
6.  Follows pawprints.\
7.  Meets cat.\
8.  Crosses bridge.\
9.  Bakery window.\
10. Asks baker.\
11. Poster with bone.\
12. Picnic in park.\
13. Children clue.\
14. Signpost with food icon.\
15. Animal shelter.\
16. Volunteer fills bowl.\
17. Bibo waits.\
18. Eats food.\
19. Brings thank-you note.\
20. Home again, happy nap.

### Example Prompt (Scene 12)

> "children's coloring page, bold clean black outlines, no shading,
> white background; Bibo the dog (small, floppy ears, round nose,
> striped collar with bone tag) discovering a **picnic blanket** in a
> sunny park; big basket, simple sandwich shapes, large apple; friendly
> scene, center composition, printable vector-like linework"

**Negative:** color, grayscale, gradients, text, clutter.

------------------------------------------------------------------------

## 8. Quality Safeguards

-   Line width ≥ 2 px (at 300 DPI).\
-   Pure B/W only.\
-   Character consistent.\
-   Enough white space.\
-   Optional captions.

------------------------------------------------------------------------

## 9. Licensing & Compliance

-   Verify **FLUX license** for commercial output.\
-   Use commercial-safe fonts.\
-   No brand logos/celebs.\
-   Add imprint & copyright page.

------------------------------------------------------------------------

## 10. MVP Milestones

1.  UI skeleton (create project, scene count, generate all).\
2.  Prompt builder + preset.\
3.  Post-process cleanup.\
4.  Per-page preview & regenerate.\
5.  PDF export with metadata.\
6.  Character consistency (seed + card).\
7.  Activity page generator.

------------------------------------------------------------------------
