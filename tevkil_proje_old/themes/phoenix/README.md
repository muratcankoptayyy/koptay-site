# Phoenix Theme Workspace

This directory contains an isolated design lab for the next-generation Tevkil UI. It allows you to iterate on a brand-new, fully responsive theme without touching the production-facing Flask application.

## Goals

- Deliver a modernized look & feel that fits Tevkil's legal services brand.
- Ensure 100% mobile compatibility with fluid layouts and accessible typography.
- Rebuild core flows (landing, onboarding, dashboard, posts, messaging, admin) using Tailwind CSS 3 and a component-driven approach.
- Ship the new theme as a drop-in replacement once stakeholder review is complete.

## Contents

```
themes/phoenix/
├── demo_app.py              # Lightweight Flask playground for the new templates
├── README.md                # You are here
├── package.json             # Front-end toolchain (Tailwind, PostCSS, autoprefixer)
├── postcss.config.cjs       # PostCSS pipeline for Tailwind
├── tailwind.config.cjs      # Tailwind configuration with Tevkil-specific design tokens
├── src/
│   └── styles/
│       └── input.css        # Tailwind entry point (imports components, utilities)
├── static/
│   ├── css/
│   │   └── main.css         # Generated Tailwind bundle (gitignored once pipeline is active)
│   ├── js/
│   │   └── interactivity.js # Alpine.js hooks & lightweight behaviors
│   ├── img/                 # Theme-specific imagery & SVG sprites
│   └── fonts/               # Optional custom typography assets
└── templates/
    └── phoenix/
        ├── layouts/         # Base layouts (shell, auth, admin, public)
        ├── components/      # Reusable UI primitives and composite blocks
        └── pages/           # Route-level templates grouped by functional area
```

> **Note**: The goal is to keep this folder completely self-contained. No production routes or assets are imported by default. You can safely iterate and run UI/UX tests here without affecting `app.py`.

## Getting Started

1. **Install front-end dependencies**
   ```powershell
   cd themes/phoenix
   npm install
   ```

2. **Start Tailwind in watch mode** (compiles `src/styles/input.css` to `static/css/main.css`)
   ```powershell
   npm run dev
   ```

3. **Run the demo Flask server**
   ```powershell
   cd ../../
   & .\venv\Scripts\Activate.ps1
   $env:FLASK_APP = "themes.phoenix.demo_app:create_app"
   $env:FLASK_ENV = "development"
   flask run --port 5050
   ```

   This launches a localhost playground at `http://127.0.0.1:5050` with mocked data so you can browse every screen in the new theme. The demo app never touches the production database by default.

4. **Build for review**
   ```powershell
   npm run build
   ```
   This produces an optimized CSS bundle inside `static/css/main.css` ready for QA or integration.

## Integration Strategy

- **Phase 1 – UX Audit & Component Inventory**: Map existing pages to their Phoenix equivalents. Document any backend data needs uncovered during the redesign.
- **Phase 2 – Component Driven Development**: Implement atomic components (buttons, inputs, cards, tables, stats) inside `templates/phoenix/components/`. Compose feature screens from these blocks.
- **Phase 3 – Blueprint Wiring**: Once the front-end is approved, port Phoenix templates into Flask blueprints that mirror the production routes. All wiring happens behind a feature flag so that QA can switch between themes safely.
- **Phase 4 – Rollout**: After end-to-end validation, replace legacy templates gradually (or provide a toggle) and ship.

## Design Principles

- **Consistency**: Shared spacing scale, color palette, and typography tokens defined in `tailwind.config.cjs`.
- **Accessibility**: High-contrast color combinations, focus-visible states, semantic markup, reduced motion options.
- **Performance**: Tree-shaken Tailwind bundle, limited external dependencies, minimal runtime JS (Alpine.js optional).
- **Mobile-first**: Layouts start with small screens, scale up with progressive enhancements (grid, flex, responsive typography).
- **Law-focused Personality**: Professional neutrals with confident accent colors, iconography tailored for legal workflows, micro-interactions that inspire trust.

## Next Steps

- Populate `components/` with core building blocks (navigation, tab strips, cards, tables, modals, toast notifications).
- Mirror critical flows inside `pages/` (landing, register, login, dashboard overview, post detail, chat thread, admin overview).
- Hook demo routes in `demo_app.py` to realistic mock data sets in `demo_data.py` for better UX evaluation.
- Share Figma references and iterate with the product/design team before hardening the markup.

Happy building! 🛠️✨
