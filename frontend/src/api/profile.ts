import { api } from './client';
export type Profile = { id: number; full_name: string; email: string; phone: string };
export const getProfile = () => api<Profile>('/profile');
export const getPreviousChecks = () => api<{name:string;status:string}[]>('/profile/checks');
