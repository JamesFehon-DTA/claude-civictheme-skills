# CivicTheme Claude Skills
**Repo Name:** `claude-civictheme-skills`

A modular repository of Claude skills designed for deterministic CivicTheme component development and sub-theme maintenance. 

## Architecture: Router-plus-Handler

This repository utilizes a distributed architecture to avoid monolithic skill decay and ensure single-responsibility logic. 

* **Router (Entry Point):** `civictheme-component-type-selector` orchestrates intent and directs the session to the appropriate handler. 
* **Handlers:**
    * **SDC Generator:** For new Single Directory Components. 
    * **Override Generator:** For sub-theme component overrides. 
    * **Style Override:** Focuses on SCSS variable architecture. 
    * **JS Enhancement:** Manages behavior and library overrides. 
    * **Paragraph Generator:** Specifically for Drupal paragraph integration. 

## Shared Reference Patterns

The handlers consume a set of canonical reference files to ensure consistency across output:

* **Component YAML:** Defined patterns for `.component.yml` structures. 
* **Twig Patterns:** Standardized markup practices, including `attributes.addClass()` for root elements. 
* **Field Naming:** Consistent Drupal field machine name conventions. 
* **Libraries & Assets:** Management of `libraryOverrides` and frontend assets. 
* **Variables:** Centralized SCSS theming tokens and variables. 

## Deterministic Principles

Skills were created by referencing CivicTheme technical facts:

* **Inheritance:** `libraryOverrides` must be explicitly redeclared in sub-theme overrides.
* **Security:** The `|raw` filter is prohibited (removed in v1.12.2).
* **Extension:** Use full replacement; `{% extends %}` is no longer supported as of v1.11.0.
* **SDC Integration:** An SDC auto-loads its own co-located library (CSS and JS from the component directory). Enhancements targeting existing CivicTheme markup without a new SDC must attach a library manually.
