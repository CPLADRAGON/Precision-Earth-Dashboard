# Design System Document: The Precision Earth Interface

## 1. Overview & Creative North Star
**Creative North Star: The Digital Agronomist**

This design system moves away from the "cluttered dashboard" trope and toward an editorial, high-authority tool that feels like a premium piece of industrial equipment. It balances the rugged, utilitarian needs of plantation management with the sophisticated data visualization of a laboratory. 

The aesthetic identity is defined by **Organic Precision**. We break the traditional "grid-of-boxes" by using intentional asymmetry, generous white space, and a high-contrast typography scale. We aren't just showing data; we are presenting a curated, authoritative narrative of soil health. By utilizing layered surfaces and removing harsh lines, the UI feels integrated into the workflow, echoing the natural layers of the earth it monitors.

---

## 2. Colors & Surface Philosophy
The palette is grounded in deep, silty greens and high-utility status tones. However, the execution must remain "High-End Editorial."

### The "No-Line" Rule
**Strict Mandate:** Designers are prohibited from using 1px solid borders to section off content. 
Structure must be defined through **Background Color Shifts**. For example:
- A `surface-container-low` section should sit directly on a `surface` background. 
- Separation is achieved through the contrast between `#F4F4EF` and `#F9FAF5`, not a line.

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers—like stacked sheets of fine, heavy-weight paper.
- **Base Level:** `surface` (#F9FAF5) for the main application background.
- **Sectioning:** `surface-container-low` (#F4F4EF) for large sidebars or secondary content areas.
- **Content Cards:** `surface-container-lowest` (#FFFFFF) to provide a "pop" of clean, white space for high-priority data.
- **Inner Accents:** `surface-container-high` (#E8E8E4) for nested elements like search bars or internal data tables.

### The Glass & Gradient Rule
To avoid a "flat" industrial feel, use **Glassmorphism** for floating elements (e.g., mobile navigation or quick-action overlays). Use semi-transparent `surface` colors with a `backdrop-blur` of 12px-16px.
- **Signature CTA Texture:** Use a subtle linear gradient (135°) from `primary` (#154212) to `primary-container` (#2D5A27) to give buttons a tactile, high-end "weighted" feel.

---

## 3. Typography
We utilize a dual-typeface system to bridge the gap between "Industrial Tool" and "Sophisticated Brand."

*   **Display & Headlines (Manrope):** Chosen for its geometric precision and modern, wide stance. Use `display-lg` and `headline-md` to announce critical plantation stats. It conveys authority and "The Big Picture."
*   **Body & Data (Inter):** The workhorse. Inter’s high x-height and technical clarity ensure that moisture percentages and soil PH levels are legible at a glance, even in high-glare outdoor environments.

**Hierarchy as Brand:** Use `title-lg` in `primary` (#154212) for section headers to ground the page in the "Earthy" brand identity, while using `label-sm` in `on-surface-variant` (#42493E) for technical metadata to keep the interface from feeling heavy.

---

## 4. Elevation & Depth
In this system, depth is a tool for focus, not just decoration.

*   **Tonal Layering:** Avoid shadows for static cards. Instead, place a `surface-container-lowest` (#FFFFFF) card on a `surface-container` (#EEEEEA) background. This creates a soft, natural lift.
*   **Ambient Shadows:** For "Floating" elements (Modals, Hover states), use extra-diffused shadows. 
    *   *Shadow Color:* 6% opacity of `on-surface` (#1A1C1A).
    *   *Blur:* 24px - 40px. 
*   **The Ghost Border:** If a boundary is strictly required for accessibility (e.g., in high-density tables), use the `outline-variant` (#C2C9BB) at **15% opacity**. Never use 100% opaque borders.
*   **Environmental Bleed:** Use 40% opacity `surface-tint` (#3B6934) in backdrop blurs to allow the underlying "green" tones of the plantation data to soften the edges of the UI.

---

## 5. Components

### Cards & Data Clusters
*   **Rule:** Forbid divider lines. 
*   **Execution:** Use `spacing-8` (1.75rem) to separate content blocks vertically. Group related data within a `surface-container-lowest` card. Use a `primary-fixed` (#BCF0AE) accent bar (4px width) on the left side of a card to indicate the "active" or "selected" plantation plot.

### Status Indicators (The Traffic Light)
*   **Critical Alert:** `error` (#BA1A1A) text on an `error-container` (#FFDAD6) pill.
*   **Warning:** `on-tertiary-fixed-variant` (#930010) on a `tertiary-fixed` (#FFDAD6) pill.
*   **Optimal:** `on-primary-fixed-variant` (#23501E) on a `primary-fixed` (#BCF0AE) pill.

### Buttons
*   **Primary:** Gradient fill (`primary` to `primary-container`). `Rounded-md` (0.375rem). No shadow.
*   **Secondary:** `outline-variant` ghost border (20% opacity). Text color `primary`.
*   **Tertiary:** Plain text in `secondary` (#005FAF) with a `spacing-1` underline on hover.

### Soil Sensor Inputs
*   **Text Fields:** `surface-container-highest` fill with a `spacing-px` bottom stroke in `outline`. On focus, the bottom stroke expands to 2px in `primary`.

### Specialized Plantation Components
*   **Moisture Gauges:** Use `secondary` (#005FAF) for moisture data. Use a semi-circular progress arc with a `secondary-fixed` background to show "Water Capacity."
*   **Health Heatmaps:** Use `primary-container` as the base, transitioning to `tertiary-container` for "Scorched/Dry" areas.

---

## 6. Do's and Don'ts

### Do
*   **Do** use asymmetrical layouts. A large `display-md` metric on the left balanced by a small, dense `body-sm` table on the right feels intentional and editorial.
*   **Do** lean into `primary-fixed` (#BCF0AE) for highlights. It’s a "bright" earth tone that feels modern and high-tech.
*   **Do** use `spacing-16` (3.5rem) for page margins. Breathing room is the hallmark of premium design.

### Don't
*   **Don't** use pure black (#000000). Use `on-surface` (#1A1C1A) to keep the "Industrial" look from feeling "Digital."
*   **Don't** use standard 1px grey dividers between list items. Use a `spacing-4` gap and a subtle `surface-variant` background shift on hover.
*   **Don't** use heavy "Drop Shadows." They look cheap. If it doesn't float with tonal layering, it shouldn't float.