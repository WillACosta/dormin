## Dormin Split Keyboard

> 3×6 (+2 outer-pinky) Split Keyboard · 3 Thumb Keys · All 1U · MX Compatible

Dormin is a 42 — 36 keys split keyboard, inspired by some awesome keyboards that I've used and loved. The main goal is to create a customizable keyboard with optional features, but still as minimal as possible regarding the design.

### Must have specs

- Wireless Ble.
- Ultra low-profile build (<= 7mm).
- Low-profile switches and keycaps.
- Compatible with MX-Standard and the Gateron KS33/3.0 Low-Profile switches & Choc V2.
- Huge battery life (1200mAh).
- Minimalist and industrial design.
- Aluminum case and plate.
- 4 different layouts trough breakaway parts.
- Split and "Unibody" layouts (Using Pogo pins)
- MX-Spacing
- Status LEDs

**Optional**

- EC12 Rotatory Encoder
- SD OLED screen or Nice!View

## Layout Overview

The Dormin is a **40-key split keyboard** (20 keys per half) with a column-staggered matrix and a splayed thumb cluster.

| Zone | Columns | Rows | Keys/half | Notes |
|------|---------|------|-----------|-------|
| Matrix | 6 (outer → inner) | 3 (bottom, home, top) | 17 | Outer column skips bottom row (2 keys only) |
| Thumb | 3 (inner, home, outer) | 1 | 3 | Splayed arc, anchored below index |
| **Total** | | | **20** | **40 keys full board** |

### Column Stagger Profile

```
         outer  pinky  ring   middle  index  inner
stagger:   —    +u/2   +u/4   +u/4   −u/4   −u/4
mm:        0    +9.525 +4.763 +4.763 −4.763 −4.763
```

```
                    ┌──┐┌──┐
               ┌──┐ │  ││  │ ┌──┐
          ┌──┐ │  │ │Mi││Mi│ │  │ ┌──┐
     ┌──┐ │  │ │Ri││dd││dd│ │In│ │  │
     │  │ │Pi│ │ng││le││le│ │ne│ │  │
     │Ou│ │nk│ │  ││  ││  │ │r │ │  │
     │te│ │y │ │  ││  ││  │ │  │ │  │
     │r │ │  │ │  ││  ││  │ │  │ │  │
     └──┘ │  │ │  │└──┘└──┘ │  │ │  │
          └──┘ └──┘          └──┘ └──┘
                    ┌──┐
               ┌──┐│  │┌──┐
               │Th ││Th││Th│
               │ 3 ││ 2││ 1│
               └──┘└──┘└──┘
```

### Thumb Cluster Geometry

| Key | Splay | Spread | Stagger | Effective rotation |
|-----|-------|--------|---------|--------------------|
| thumb_inner | 0° | u (19.05mm) | 0mm | 0° |
| thumb_home | −15° | u+2.5 (21.55mm) | −2.7mm | −15° |
| thumb_outer | −14° | u+2.5 (21.55mm) | −2.5mm | −29° |

The thumb cluster anchors at `matrix_index_bottom` with a `[-0.1u, -1.30u]` offset, placing it slightly left and well below the index column — a natural resting position for the thumb.
