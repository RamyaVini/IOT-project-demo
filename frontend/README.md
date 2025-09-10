## PV Events App (Next.js)

A Next.js 15 app using the App Router. Includes Docker support for production and a stable Webpack build (Turbopack disabled for builds due to known Docker issues).

### Requirements
- Node.js 22+ (project Dockerfile uses `node:22-slim`)
- npm 10+

### Install
```bash
npm ci
```

### Local Development
```bash
npm run dev
# opens http://localhost:3000
```

### Production Build & Run (host machine)
```bash
npm run build
npm run start
# serves on http://localhost:3000
```

### Docker

Production image (multi-stage, non-root):
```bash
docker build -t iot-frontend .
docker run --rm -p 3000:3000 iot-frontend
```

Development image (optional):
You can override the command to run the dev server within the container:
```bash
docker run --rm -p 3000:3000 iot-frontend npm run dev
```

If you want a dedicated dev target with live reload and volume mounts, add a `dev` stage to the Dockerfile or mount your source:
```bash
# Windows PowerShell from project root
docker run --rm -p 3000:3000 -v ${PWD}:/app -v /app/node_modules iot-frontend npm run dev
```

### Scripts
- `dev`: Next dev server with Turbopack for fast HMR
- `build`: Production build (Webpack)
- `start`: Production server (after build)
- `lint`: Run eslint

### Environment Variables
Create `.env.local` for local development (not committed):
```
# Example
NEXT_PUBLIC_API_BASE_URL=http://localhost:4000
```

In Docker/production, use `-e VAR=value` or a secrets manager.

### Why different NODE_ENV per stage?
The Dockerfile uses:
- `deps` stage: `NODE_ENV=development` to install devDependencies (build tools like Next/Tailwind/PostCSS).
- `builder` stage: `NODE_ENV=production` so Next optimizes the build.
- `runner` stage: `NODE_ENV=production` for a lean runtime image.

This keeps builds reliable and the final image small.

### Troubleshooting
- Turbopack error during Docker build (e.g., "TurbopackInternalError: Failed to write page endpoint /_error"):
  - The project uses Webpack for `npm run build`. If you see cache issues, rebuild without cache:
    ```bash
    docker build --no-cache -t iot-frontend .
    ```
- Port already in use:
  - Stop the conflicting process or use a different port mapping, e.g. `-p 8080:3000`.
- Changed dependencies not picked up in Docker:
  - Rebuild without cache or bump `package.json` to invalidate the deps layer.

### Project Structure
```
src/
  app/
    page.tsx         # Home page
    layout.js        # App layout
public/              # Static assets
```

### License
MIT

This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://github.com/vercel/next.js/tree/canary/packages/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.js`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
