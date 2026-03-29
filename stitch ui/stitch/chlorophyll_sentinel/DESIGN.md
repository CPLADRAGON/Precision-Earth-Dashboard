# Design System Document: The Bioluminescent Nexus

## 1. Overview & Creative North Star
**Creative North Star: "The Digital Greenhouse"**

This design system moves away from the "industrial dashboard" trope and toward a high-end, editorial experience that feels like a living organism. It treats data not as static numbers, but as vital signs. We achieve this through **Organic Technocracy**: a marriage of high-tech precision (Space Grotesk typography, glassmorphism) and organic depth (layered navy surfaces, vibrant green glows).

To break the "template" look, we abandon rigid grids in favor of **Intentional Asymmetry**. Large-scale KPI cards should overlap subtle background gradients, and data tables should feel like floating panes of glass rather than boxed-in spreadsheets. We prioritize "breathing room" (negative space) to ensure that even in a data-rich environment, the user feels a sense of calm and control.

---

## 2. Colors & Surface Philosophy
The palette is rooted in the "Bioluminescent Dark" aesthetic—deep, atmospheric navies punctuated by high-energy chlorophyll greens.

### Surface Hierarchy & Nesting
We do not use flat surfaces. Depth is achieved through a "Stacked Glass" metaphor:
*   **Background (`#101319`):** The deep soil. The absolute base.
*   **Surface (`#101319`):** The primary canvas for layout.
*   **Surface-Container-Low (`#191C22`):** Used for large structural zones (e.g., Sidebar background).
*   **Surface-Container (`#1D2026`):** The standard card base.
*   **Surface-Container-Highest (`#32353C`):** Used for interactive elements or "popped" states.

### The "No-Line" Rule
**Explicit Instruction:** Prohibit 1px solid borders for sectioning. Boundaries must be defined solely through background color shifts or subtle tonal transitions. A `surface-container-low` card sitting on a `surface` background provides enough contrast to be felt without being seen as a "box."

### The "Glass & Gradient" Rule
Floating elements (Modals, Hover states, Tooltips) must use **Glassmorphism**. 
*   **Recipe:** `surface-container-highest` at 60% opacity + `backdrop-filter: blur(12px)`.
*   **Signature Textures:** Main CTAs and Primary KPI trends should use a linear gradient: `primary` (`#78DC77`) to `primary-container` (`#4CAF50`). This adds a "pulse" to the data.

---

## 3. Typography
We use a dual-typeface system to balance high-tech precision with editorial readability.

*   **Display & Headlines (Space Grotesk):** This is our "Precision" font. Use `display-lg` (3.5rem) for critical soil health percentages. Its geometric nature feels futuristic and high-tech.
*   **Body & Titles (Manrope):** This is our "Humanistist" font. It provides high legibility for dense data tables and long-form insights.

**Hierarchy as Identity:**
*   **Hero KPI:** `display-lg` / `primary` color.
*   **Section Header:** `headline-sm` / `on-surface`.
*   **Secondary Label:** `label-md` / `on-surface-variant` (uppercase with 0.05em letter spacing).

---

## 4. Elevation & Depth
In this system, light is the primary communicator of importance.

### The Layering Principle
Avoid shadows on standard cards. Instead, use the **Tonal Stacking**:
1.  **Level 0:** `surface` (The Floor)
2.  **Level 1:** `surface-container-low` (The Zone)
3.  **Level 2:** `surface-container` (The Card)

### Ambient Shadows & "Ghost Borders"
When an element must "float" (e.g., a dropdown or active sensor detail):
*   **Shadow:** 0px 20px 40px rgba(0, 0, 0, 0.4). Shadows should be tinted with the background hue, never pure black.
*   **Ghost Border:** If contrast is insufficient, use a 1px border of `outline-variant` at **15% opacity**. This creates a "specular highlight" on the edge of the glass rather than a physical containment line.

---

## 5. Components

### KPI Cards with Health Indicators
*   **Structure:** No borders. Background: `surface-container`. 
*   **Visual:** A subtle `primary` glow (5% opacity) radiating from the top-left corner.
*   **Transition:** On hover, the background shifts to `surface-container-high` and the `primary` accent glow intensifies.

### Interactive Charts
*   **Line Art:** Use `primary` for healthy data. Use `tertiary` (`#FFB1C7`) for warning zones.
*   **Fill:** Use a gradient from `primary` (20% opacity) to transparent.
*   **Data Points:** On hover, points should expand and emit a `primary_fixed` glow.

### Sophisticated Data Tables
*   **Rule:** Forbid the use of divider lines. 
*   **Structure:** Use vertical whitespace (Spacing Scale `4` or `5`) to separate rows.
*   **Alternating Tones:** Use `surface-container-lowest` for the header row and `surface` for body rows.
*   **Selection:** Active rows use a `surface-variant` background with a 2px `primary` left-accent bar.

### Buttons & Chips
*   **Primary Button:** Gradient (`primary` to `primary-container`), `md` (0.75rem) corner radius. Typography: `title-sm` (bold).
*   **Filter Chips:** `surface-container-highest` background, no border. When active, use `primary-fixed` text on `on-primary-fixed-variant` background.

---

## 6. Do's and Don'ts

### Do:
*   **Embrace Breath:** Use Spacing Scale `12` (2.75rem) or `16` (3.5rem) between major dashboard modules.
*   **Layer with Intent:** Ensure nested components are always a step "brighter" or "darker" than their parent container.
*   **Use Subtle Animation:** All hover states should have a `200ms ease-out` transition.

### Don't:
*   **Don't use pure white:** Use `on-surface` (`#E1E2EB`) for text to prevent eye strain in dark environments.
*   **Don't use 100% opaque borders:** They shatter the glassmorphism illusion.
*   **Don't clutter:** If a screen feels busy, increase the spacing scale rather than adding dividers.
*   **Don't use standard "Red":** Use the `error` token (`#FFB4AB`) which is tuned for dark-theme luminance.