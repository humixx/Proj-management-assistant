# Frontend - Project Management Assistant

Next.js frontend application with TypeScript and Tailwind CSS.

## Getting Started

### Prerequisites
- Node.js 18+ and npm/yarn/pnpm

### Installation

1. Install dependencies:
```bash
npm install
# or
yarn install
# or
pnpm install
```

2. Create a `.env.local` file (copy from `.env.example` if available):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

3. Run the development server:
```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

- `src/app/` - Next.js App Router pages
- `src/components/` - React components
- `src/lib/` - Utilities, API clients, and stores
- `src/hooks/` - Custom React hooks
- `src/types/` - TypeScript type definitions
- `src/utils/` - Utility functions

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS framework
- **Zustand** - State management
- **Axios** - HTTP client
- **Socket.io Client** - WebSocket client

