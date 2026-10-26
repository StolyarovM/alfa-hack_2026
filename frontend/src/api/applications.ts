import { api } from './client';

export type Application = {
  id: number;
  product_type: string;
  requested_amount: number;
  status: string;
  outcome?: string | null;
  risk?: number | null;
  created_at: string;
  checks: {
    name: string;
    status: string;
    message: string;
  }[];
};

export type ApplicationChatResponse = {
  reply: string;
};

export const getApplications = () =>
  api<Application[]>('/applications');

export const getApplication = (id: string) =>
  api<Application>(`/applications/${id}`);

export const createApplication = (payload: unknown) =>
  api<Application>('/applications', {
    method: 'POST',
    body: JSON.stringify(payload),
  });

export const chatWithApplication = (
  id: string,
  message: string,
) =>
  api<ApplicationChatResponse>(
    `/applications/${id}/chat`,
    {
      method: 'POST',
      body: JSON.stringify({ message }),
    },
  );