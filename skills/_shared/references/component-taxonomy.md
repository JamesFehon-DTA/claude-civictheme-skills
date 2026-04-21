# CivicTheme Component Taxonomy

All components shipped in the CivicTheme UIKit (1.12.x). Use this reference to:

- Confirm whether a requested component already exists in the base theme before classifying as `new_sdc_component` vs `override_existing_civictheme_component`
- Identify CSS-only components — they have no Twig template and affect story pattern selection (see `storybook-patterns.md`)

## 01-Atoms — 24 components

| Category | Components |
|---|---|
| Form controls | Button, Checkbox, Field Description, Field Message, Fieldset, Input, Label, Radio, Select, Textarea, Textfield |
| Typography | Heading, Paragraph, Link, Content Link |
| Taxonomic/status | Chip, Tag |
| Media | Image, Iframe, Video |
| Data display | Table, **Table Sort** *(CSS-only)*, **Summary List** *(CSS-only)* |
| Overlay | Popover |

**Table Sort** is CSS-only with no `theme` prop and no dark story — it is invisible on dark backgrounds. This is a known gap.
**Summary List** is CSS-only; dark is handled via a separate dark story (Pattern B).

## 02-Molecules — 33 components

| Category | Components |
|---|---|
| Cards | Event Card, Fast Fact Card, Navigation Card, Promo Card, Publication Card, Service Card, Subject Card |
| Filtering/search | Single Filter, Group Filter, Inline Filter, Search |
| List furniture | Snippet, Pagination |
| Rich content | Basic Content, Callout, Accordion, Figure, Attachment |
| Navigation/wayfinding | Breadcrumb, Back To Top, Table Of Contents, Next Steps, Feature Link List |
| Identity | Logo, Social Links |
| Form | Field, Tooltip |
| Media | Video Player, Map |
| Interaction | Tabs |
| Taxonomy | Tag List |

## 03-Organisms — 15 components

| Category | Components |
|---|---|
| Page chrome | Header, Footer |
| Navigation | Navigation, Mobile Navigation, Side Navigation |
| Hero/feature | Banner, Campaign, Promo |
| Content collections | List, Filterable Table, Slider |
| Alerts/feedback | Alert, Message |
| Forms | Webform |
| Accessibility | Skip Link |

## 04-Templates — 1 component

| Category | Components |
|---|---|
| Page layout | Page |
