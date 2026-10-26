
const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('credit_token');
  const response = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...init.headers }
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    // Если сервер отклонил уже сохранённый токен, сбрасываем сессию и возвращаем пользователя к входу.
    if (response.status === 401 && token) {
      localStorage.removeItem('credit_token');
      window.dispatchEvent(new Event('credit:unauthorized'));
    }
    throw new Error(body.detail || `Ошибка API: ${response.status}`);
  }
  return response.status === 204 ? undefined as T : response.json();
}
