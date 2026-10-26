import { api } from './client';
export type RegisterPayload = { full_name: string; email: string; phone: string; password: string };
export async function login(username: string, password: string) {
  const result = await api<{access_token:string; token_type:string}>('/auth/login', {method:'POST', body:JSON.stringify({username,password})});
  localStorage.setItem('credit_token', result.access_token); return result;
}
export async function register(payload: RegisterPayload) {
  const result = await api<{access_token:string; token_type:string}>('/auth/register', {method:'POST', body:JSON.stringify(payload)});
  localStorage.setItem('credit_token', result.access_token); return result;
}
export function logout() { localStorage.removeItem('credit_token'); }
export function tokenExists() { return Boolean(localStorage.getItem('credit_token')); }
