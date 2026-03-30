# Debt Payoff Calculator (TanStack DB + Electric SQL Demo)

This is a debt payoff calculator built to demonstrate the power of [TanStack DB](https://tanstack.com/db) combined with [Electric SQL](https://electric-sql.com/) for real-time sync.

It helps users organize their debts, choose a payoff strategy (Avalanche vs. Snowball), and visualize their journey to becoming debt-free.

## 📺 Deep Dive

I recorded a deep dive video explaining how this app works and how TanStack DB integrates with Electric SQL.

https://www.youtube.com/watch?v=ae05QlM50DI

## 🚀 Tech Stack

- **Framework:** [TanStack Start](https://tanstack.com/start)
- **State/Sync:** [TanStack DB](https://tanstack.com/db) + [Electric SQL](https://electric-sql.com/)
- **Database:** PostgreSQL (ORM: [Prisma](https://www.prisma.io/))
- **Auth:** [Better Auth](https://better-auth.com/)
- **Styling:** [Tailwind CSS](https://tailwindcss.com/) + [shadcn/ui](https://ui.shadcn.com/)

## ✨ Features

- **Zero Latency:** Data is updated locally instantly, providing a snappy user experience while syncing happens in the background.
- **Real-time Sync:** Multi-device synchronization powered by Electric SQL.
- **Payoff Strategies:** Compare "Snowball" (lowest balance first) vs. "Avalanche" (highest interest first) methods.
- **Visualizations:** Interactive charts and schedules to see exactly when each debt will be paid off.

## 🛠️ Getting Started

Follow these steps to get the app running locally.

### Prerequisites

- Node.js & pnpm
- Docker (for the database and Electric sync service)

### 1. Install Dependencies

```bash
pnpm install
```

### 2. Configure Environment Variables

Create a `.env.local` file in the root directory and add your [Google OAuth credentials](https://www.better-auth.com/docs/authentication/google) (for authentication):

```env
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

### 3. Start Backend Services

Start PostgreSQL and Electric SQL using Docker Compose:

```bash
pnpm dc:up
```

### 4. Setup Database

Apply the Prisma schema to your local PostgreSQL instance:

```bash
pnpm db:migrate dev
```

### 5. Run the App

Start the development server:

```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 💡 How it Works

1.  **PostgreSQL** acts as the source of truth.
2.  **Electric SQL** sits in front of Postgres, providing a sync layer that syncs data to the client.
3.  **TanStack DB** runs in the browser and manages the local database.
4.  **Server Functions** are used to persist changes to the database.

## 📝 License

MIT
