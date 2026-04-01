# FRONTEND_STYLE_GUIDE — Answer Engine

---

## 1. Purpose

This document defines the minimal frontend styling and UI consistency rules for the Answer Engine.

It ensures:
- visual consistency
- predictable UI behavior
- clean developer experience during iteration

This is intentionally minimal for V1 and can be extended later.

---

## 2. Core Principles

### 2.1 Dark Theme Only (V1)

The application must use a dark theme by default.

There is no light mode in V1.

Reason:
- better readability for developer-focused usage
- consistency across all screens
- reduced design complexity

---

### 2.2 Functional over Decorative

UI should prioritize:
- clarity
- usability
- readability

Avoid:
- heavy animations
- unnecessary visual effects
- complex styling

---

### 2.3 Consistency over Creativity

All components must follow consistent:
- spacing
- colors
- button behavior
- layout structure

---

## 3. Layout Structure

The V1 UI is centered on a main question/answer surface with an optional inspect panel.

MAIN SURFACE:
- question input
- answer output
- clear answer state and limitations when present

OPTIONAL INSPECT / SIDE PANEL:
- sources panel
- context viewer
- trace / debug panel
- verification details

This layout should remain simple, stable, and developer-friendly in V1.

---

## 4. Color System (Dark Theme)

### Backgrounds

- primary background: very dark (near black)
- secondary panels: slightly lighter dark
- cards: distinct but subtle contrast

---

### Text

- primary text: high contrast (white / near white)
- secondary text: muted gray
- disabled text: low contrast gray

---

### Accent

- primary accent color: used for active elements
- hover states: slightly brighter accent
- focus states: visible but minimal

---

## 5. Button System

Buttons must follow semantic types.

---

### 5.1 Primary Button

Usage:
- main actions (send, confirm)

Style:
- solid background
- high contrast text

---

### 5.2 Secondary Button

Usage:
- non-critical actions

Style:
- outlined or low-emphasis

---

### 5.3 Danger Button

Usage:
- delete actions
- destructive operations

Style:
- red color
- must be clearly distinguishable

---

### 5.4 Disabled State

- reduced opacity
- no hover effect
- non-clickable

---

## 6. Main Surface Rules

### Question Input

- clearly separated from the answer surface
- must support multiline input
- primary action should be obvious

---

### Answer Surface

- answer content must be easy to scan
- source-backed output should feel primary
- limitations or uncertainty must be visible without opening inspect mode
- the final answer surface should display verified output only
- do not present draft, preview, or provisional answer text in V1

---

### Optional Conversation Support

- conversation or history UI may exist later
- it is not the primary V1 layout model
- do not make the interface thread-first by default

---

## 7. Panels

### 7.1 Inspect Panel

Contains:
- sources
- context
- trace
- verification details

Must support:
- tabbed or section-based view
- scrollable content
- structured data display

---

## 8. Developer / Debug View (Important)

The UI must support visibility of:

- run progress / pipeline status
- inferred scopes
- retrieved chunks
- context pack
- pipeline trace
- verification result

This can be:
- a dedicated panel
- or a toggleable debug mode

Status visibility may include:
- scope inference running
- retrieval running
- answer generation running
- verification running

---

## 9. Spacing & Layout

- consistent padding across components
- avoid cramped UI
- prefer readable spacing over compactness

---

## 10. Typography

- simple sans-serif font
- no decorative fonts
- consistent font sizes

---

## 11. Icons (Optional)

- minimal usage
- only where it improves clarity
- avoid clutter

---

## 12. Responsiveness (V1)

Not a priority.

Focus:
- desktop layout
- developer usage

---

## 13. Extension Rules

New UI elements must:
- follow existing color and spacing rules
- reuse button styles
- not introduce new visual paradigms

---

## 14. Summary

The frontend should be:

- dark
- simple
- consistent
- functional
- developer-friendly

It is NOT:
- a marketing UI
- a consumer-grade polished product
- visually experimental
- a chat-thread-first product UI

It is a working interface for a high-trust answering system.
