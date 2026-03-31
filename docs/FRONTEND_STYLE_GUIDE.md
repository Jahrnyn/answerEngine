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

The UI follows a 3-column layout:

LEFT:
- conversation list
- session management

CENTER:
- chat interface
- message stream
- input area

RIGHT:
- sources panel
- context viewer
- trace / debug panel

This layout must remain stable across iterations.

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

## 6. Chat UI Rules

### Messages

- user messages: right-aligned
- assistant messages: left-aligned

---

### Message Blocks

- clear separation between messages
- consistent padding
- readable line spacing

---

### Input Area

- fixed at bottom
- clearly separated from chat
- must support multiline input

---

## 7. Panels

### 7.1 Left Panel

- list-based layout
- scrollable
- active item clearly highlighted

---

### 7.2 Right Panel

Contains:
- sources
- context
- trace

Must support:
- tabbed or section-based view
- scrollable content
- structured data display

---

## 8. Developer / Debug View (Important)

The UI must support visibility of:

- inferred scopes
- retrieved chunks
- context pack
- pipeline trace
- verification result

This can be:
- a dedicated panel
- or a toggleable debug mode

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

It is a working interface for a high-trust answering system.