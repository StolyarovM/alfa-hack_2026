
import { api } from './client';
export type Application = { id: number; product_type: string; requested_amount: number; status: string; outcome?: string | null; risk?: number | null; scoring_reason?: string | null; conditions?: string | null; created_at: string; checks: {name: string; status: string; message: string}[] };
export const getApplications = () => api<Application[]>('/applications');
export const getApplication = (id: string) => api<Application>(`/applications/${id}`);
export const createApplication = (payload: unknown) => api<Application>('/applications', { method: 'POST', body: JSON.stringify(payload) });
