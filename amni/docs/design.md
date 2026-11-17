# AMNI design direction

The frontend draws on Sucuri’s dark teal security presentation and Chainjobs’
warm cream surfaces, rounded typography, outlined controls, and playful graphics.
The composition, illustrations, copy, and AMNI monogram are original.

The custom AMNI mark combines an A with a check, and appears consistently in the
header and footer. The hero uses a connected support illustration with clickable
case and knowledge-base cards. Animated connection paths and a blinking support
unit add restrained motion, disabled when reduced motion is requested.

Mint, lavender, and yellow identify case management, diagnostics, and knowledge.
The case queue uses readable subjects, clear status badges, and visible search
and filter controls. Layouts adapt across mobile, tablet, and desktop sizes.

Case creation, case search, status changes, topic filters, guide dialogs, and a
sample diagnostic preview are interactive. Cases persist in browser localStorage
when available. No backend, real probe, authentication service, or AWS resources
are connected in this frontend preview.

## Preview and verification

- [Desktop preview](previews/desktop.png)
- [Mobile preview](previews/mobile.png)

The production export and TypeScript checks pass. Browser verification covered
375, 390, 768, 1024, and 1440 pixel widths without horizontal overflow. Case
creation, persistence, search, status filters and transitions, topic filters,
guide dialogs, the diagnostic preview, architecture dialog, and mobile navigation
passed with no browser errors.

The build script uses Webpack because this environment blocks a local subprocess
port used by Turbopack. This does not change the frontend framework or behavior.
