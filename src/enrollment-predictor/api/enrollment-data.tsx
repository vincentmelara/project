// pages/api/enrollment-data.ts

import type { NextApiRequest, NextApiResponse } from 'next';
import prisma from './prisma';
import { EnrollmentData, ErrorResponse } from '../types/types';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<EnrollmentData[] | ErrorResponse>
) {
  if (req.method !== 'GET') {
    res.setHeader('Allow', 'GET');
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  try {
    const enrollments = await prisma.enrollmentData.findMany({
      orderBy: {
        year: 'asc',
      },
      select: {
        id: true,
        year: true,
        students: true,
        createdAt: true,
        updatedAt: true,
      },
    });

    res.status(200).json(enrollments);
  } catch (error: any) {
    console.error('Error fetching enrollment data:', error);
    res.status(500).json({ error: 'Failed to fetch enrollment data.' });
  }
}
