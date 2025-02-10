// lib/prisma.ts

import { PrismaClient } from '@prisma/client';

declare global {
  // Prevent multiple instances of Prisma Client in development
  // This is a workaround for Next.js hot-reloading
  // https://www.prisma.io/docs/support/help-articles/nextjs-prisma-client-dev-practices
  var prisma: PrismaClient | undefined;
}

const prisma = global.prisma || new PrismaClient();

if (process.env.NODE_ENV !== 'production') global.prisma = prisma;

export default prisma;
