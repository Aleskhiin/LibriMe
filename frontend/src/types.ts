import type { JobRecord } from './api';

export interface JobEntry extends Omit<JobRecord, 'createdAt'> {
  createdAt: Date;
}
