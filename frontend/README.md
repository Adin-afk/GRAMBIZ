# Frontend - GramBiz

React + TypeScript + Vite + Tailwind CSS v4. Talks to the FastAPI backend
in `../backend`.

## Setup

```bash
npm install
cp .env.example .env   # edit VITE_API_BASE_URL if your backend isn't on :8000
npm run dev             # http://localhost:5173
```

## Build

```bash
npm run build            # outputs to dist/
npm run preview          # serve the production build locally
```

## Pages implemented

- `/login`, `/register` - JWT auth against the backend
- `/dashboard` - session summary + quick actions
- `/location` - Maharashtra > Solapur > Taluka > Village selector (fetched
  from the API, never hard-coded) + available capital input
- `/recommend` - "What business should I start?" ranked list with the
  per-component opportunity-score breakdown
- `/financial-calculator` - deterministic project cost / loan amount /
  EMI / full repayment schedule
- `/schemes` - loan scheme reference cards
- `/map` - Leaflet map with the selected village, 5/10km radius circle,
  and real PostGIS-backed nearby businesses/markets
- `/reports/:id` - saved assessment / advisory report view

## Design notes

Deliberately avoids the generic "AI SaaS dashboard" look per the project
brief: no gradients, no glassmorphism, minimal border-radius, restrained
color use. Palette is a deep navy + muted ochre accent on a paper-white
background; typography pairs a serif display face (Source Serif 4) with
IBM Plex Sans for body text and IBM Plex Mono for all monetary/score
figures (tabular numbers). Every piece of non-verified data carries an
explicit VERIFIED/DEMO/UNVERIFIED badge - this is not decorative, it's
required by the project's no-fake-data policy.

## Known limitations

- Selected location/capital lives in React context only - it resets on a
  hard page reload. Worth persisting to localStorage in a later pass.
- Map tiles require internet access to `tile.openstreetmap.org` at
  runtime (not needed at build time).
- No i18n/translation files wired up yet (English only) - the spec calls
  for Marathi/Hindi support via i18n files, not yet implemented.
- Admin dashboard, CSV import UI, and saved-assessments list page are not
  built yet.
