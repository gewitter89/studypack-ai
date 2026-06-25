# StudyPack AI Max — Research & Licenses

## 1. Open-Source Solutions Studied

### word-search-generator (joshbduncan)
- URL: https://github.com/joshbduncan/word-search-generator
- License: **MIT**
- Status: **Can use as dependency**
- Notes: Python package for generating word search puzzles. Supports custom word lists, difficulty levels, directions, masks, and PDF export. MIT license allows full integration, modification, and commercial use. We can import as a dependency or adapt the algorithm.

### math-worksheet-generator (januschung)
- URL: https://github.com/januschung/math-worksheet-generator
- License: Not explicitly stated (no LICENSE file)
- Status: **Do not copy — no license**
- Notes: Creates basic addition/subtraction/multiplication/division practice with answer sheets. Without an explicit license, default copyright applies. Can use as inspiration for our own math generator.

### math_exam_generator (matkoniecz)
- URL: https://github.com/matkoniecz/math_exam_generator
- License: Not explicitly stated
- Status: **Do not copy — no license**
- Notes: Uses Sympy and LaTeX. Good reference for design patterns (parameterized exam generation, solution keys). We will implement our own version using Python-native math.

### flash_card_generator (peterhuszar)
- URL: https://github.com/peterhuszar/flash_card_generator
- License: Not explicitly stated
- Status: **Do not copy — no license**
- Notes: Converts Excel input to DOCX flashcards. Pattern of input-table → cards → summary is useful conceptually.

### MazeMath (rogers-cyber)
- URL: https://github.com/rogers-cyber/MazeMath
- License: **Custom commercial** — prohibits resale/rebranding as competing product
- Status: **Do not use — incompatible license**
- Notes: Desktop app with arithmetic maze puzzles, live preview, PDF/JPG export. Interesting pattern for step-by-step solution. Can only use as inspiration for our own maze generator (DFS/backtracking).

## 2. Dependencies Added

| Package | License | Purpose | Status |
|---------|---------|---------|--------|
| customtkinter | MIT | Modern UI over tkinter | Added Stage 1 |
| word-search-generator | MIT | Word search puzzle generation | Under consideration for Stage 3 |

## 3. Design Patterns (not code, adapted from research)

- OpenEduCat: subject/grade/topic selection → generation → review/edit → export
- MagicSchool: worksheet generation from text/theme, grade-level tuning
- Monsha: source material import → multi-format export
- MazeMath: offline desktop app with live preview

## 4. Prohibited Actions

- Copying code from repos without explicit open-source license
- Using GPL-licensed code in closed-source commercial distribution
- Copying branded characters, illustrations, or worksheet designs
- Using names of known brands/IP in generated content
- Promising medical/psychological diagnostic value

## 5. Own Implementation Commitment

All template content, card designs, maze algorithms, math generators, editorial pass rules are our own original implementation. The architecture draws inspiration from industry patterns but is built from scratch for StudyPack AI.

## 6. NUSh (НУШ) Reference

- Source: https://mon.gov.ua/osvita-2/zagalna-serednya-osvita/osvitni-programi/navchalni-programi-dlya-1-4-klasiv
- Ministry of Education publishes standard programs for grades 1-4 (Savchenko and Shiyan programs)
- We do NOT claim official certification — only "oriented toward primary school / NUSh level"
