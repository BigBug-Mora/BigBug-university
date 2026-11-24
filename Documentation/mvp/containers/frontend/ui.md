# EstateFlow UI

Follow the [Courtyard House showcase](../../showcase/index.html) for the MVP’s visual design. Use generous spacing, large photos, and thin dividers on public property pages. Use tighter spacing for search, chat, and seller tools.

## Theme

Use **Instrument Serif** for display headings and **DM Sans** for body text, navigation, and controls.

| Role | Light | Dark |
| --- | --- | --- |
| Background | `#F7F4EB` | `#21231D` |
| Text | `#252A21` | `#F3F0E6` |
| Muted text | `#605F52` | `#C0BCAE` |
| Borders and dividers | `#D8D2C3` | `#4D5042` |
| Primary action | `#36492E` | `#C9D5AE` |
| Text on primary action | `#F7F4EB` | `#252A21` |

Use shared CSS variables to apply the palette to both shadcn/ui controls and Tailwind layouts. [shadcn/ui theming](https://ui.shadcn.com/docs/theming)

## Layout and accessibility

- Pair showcase photos with short text in alternating columns. Stack each photo above its text on narrow screens.
- Make search results easy to scan with consistent photo proportions and predictable placement of price, location, and key facts.
- Label controls, keep keyboard focus visible, and pair status colors with text.

See the [frontend spec](frontend.md) for screen behavior and the [MVP tech stack](../../teach-stack/tech-stack.md#1-technology-stack) for tooling.
