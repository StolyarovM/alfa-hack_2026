
import { api } from './client';
export type Product = { id: string; name: string; type: string; description: string; min_amount: number; max_amount: number; term_months: number };
export const getProducts = () => api<Product[]>('/products');
export const recommendProduct = (payload: unknown) => api<{recommendations: Product[]; explanation: string}>('/products/recommend', { method: 'POST', body: JSON.stringify(payload) });
