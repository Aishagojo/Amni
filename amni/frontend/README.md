# AMNI frontend

The interactive frontend for AMNI, a technical support platform built with
**Next.js, React, TypeScript, and Tailwind CSS**.

> This is a frontend prototype. Cases use browser storage, diagnostics display
> sample output, and no FastAPI service, database, authentication system, or
> WebSocket connection is integrated yet.

See the [main project README](../../README.md) for project status, the roadmap,
and setup instructions.

## Run locally

Requires **Node.js 20.9+** and npm. From this directory:

```sh
npm ci
npm run dev
```

Open **[http://localhost:3000](http://localhost:3000)**. If Next.js reports an
existing server for this directory, open its printed URL instead of starting
another instance. Stop the existing server with Ctrl+C before changing ports.

## Check and build

```sh
npm run typecheck
npm run build
```

| Script | Behavior |
| --- | --- |
| `dev` | Starts Next.js with hot reload. |
| `typecheck` | Runs `tsc --noEmit`. |
| `build` | Runs `next build --webpack` and exports the site to `out/`. |

The application uses a static export rather than `next start`. To preview the
production output with Python:

```sh
python3 -m http.server 8080 --directory out
```

Open **[http://localhost:8080](http://localhost:8080)**, or serve `out/` with another
static HTTP server. No environment variables or cloud credentials are needed.

## Source guide

| Path | Responsibility |
| --- | --- |
| [`app/page.tsx`](app/page.tsx) | Homepage, case interactions, navigation, dialogs, and preview state. |
| [`app/layout.tsx`](app/layout.tsx) | Root document, metadata, and stylesheet imports. |
| [`app/globals.css`](app/globals.css) | Base styles and shared layout rules. |
| [`app/brand-theme.css`](app/brand-theme.css) | AMNI colors, typography, illustration styling, and responsive presentation. |
| [`app/icon.svg`](app/icon.svg) | Application icon using the custom AMNI mark. |
| [`components/brand.tsx`](components/brand.tsx) | Shared AMNI monogram and wordmark. |
| [`components/support-scene.tsx`](components/support-scene.tsx) | Interactive support illustration. |
| [`lib/demo.ts`](lib/demo.ts) | Sample cases, guides, shared case types, and planned architecture content. |
| [`public/fonts/`](public/fonts/) | Self-hosted Manrope font and its license. |
| [`next.config.ts`](next.config.ts) | Static-export configuration. |

## Demo behavior

- Create cases, search the queue, filter by status, and update case status.
- Save case changes under the `amni-demo-cases` localStorage key when storage is
  available; otherwise, changes remain in the current page session.
- Filter knowledge-base topics and open sample guides.
- Run the diagnostic preview to display simulated results without executing
  commands or making network probes.

Browser storage is specific to the origin. Switching ports creates a separate
demo workspace. Reset instructions are in the
[main README](../../README.md#demo-data).

## Validation scope

The production export, TypeScript checks, and browser interaction checks have
passed. Responsive checks covered 375, 390, 768, 1024, and 1440 pixel widths.
Backend behavior, authentication, live diagnostics, and deployment are outside
this prototype's verification scope.
