@promplet version: 0.7

@module weavemark.domains.programming.stacks.typescript_nextjs_prisma_sqlite

# Tech Stack: TypeScript + Next.js + Prisma + SQLite

### Frontend
- **Framework**: Next.js 14+ with App Router.
- **Language**: TypeScript 5+ with strict mode and no `any`.
- **Styling**: Tailwind CSS with design tokens in `tailwind.config.ts`.
- **State**: React Server Components by default; client state via Zustand where
  needed for local UI state.
- **Forms**: react-hook-form with zod validation schemas shared with API and
  Server Actions.
- **Data fetching**: Server Actions for mutations and `fetch` in Server
  Components for reads.

### Backend
- **Runtime**: Node.js runtime only. Do not use Edge runtime for routes or actions
  that touch SQLite.
- **ORM**: Prisma with SQLite provider.
- **Validation**: zod schemas shared between client and server.
- **Local configuration**: `DATABASE_URL` MUST point to a local SQLite file,
  normally under the app workspace or OS user-data directory.
- **Process model**: one local app server owns SQLite writes. If packaged for
  desktop use, the desktop shell starts and supervises that server.

### Database
- **Engine**: SQLite 3 in WAL mode.
- **Migrations**: Prisma Migrate. The app MUST run pending migrations on startup
  after creating a backup when existing data is present.
- **Naming**: camelCase in Prisma schema, mapped to snake_case table/column names
  where practical.
- **Soft deletes**: `deletedAt DateTime?` field for recoverable entities.
- **Audit fields**: `createdAt DateTime @default(now())`, `updatedAt DateTime @updatedAt`.
- **Transactions**: multi-entity updates MUST use explicit transactions.

### Testing
- **Unit**: Vitest with happy-dom for component tests.
- **API/storage**: Vitest using temporary SQLite files and isolated data
  directories.
- **E2E**: Playwright for critical local user flows.
- **Coverage**: minimum 80% line coverage for application logic.

### Deployment
- **Target**: local Node.js process, self-hosted single-user service, or optional
  Electron/Tauri wrapper.
- **Not supported by default**: serverless deployments whose filesystem is
  ephemeral or shared across users.
- **Config**: environment variables via `env.mjs` with zod validation at startup.
- **Health check**: `GET /api/health` returning local store status, schema
  version, and app version.
