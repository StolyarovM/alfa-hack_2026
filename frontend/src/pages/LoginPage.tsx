import { useState } from 'react';
import { login, register } from '../api/auth';

export default function LoginPage({ onLogin }: { onLogin: () => void }) {
  const [mode, setMode] = useState<'login'|'register'>('login');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError('');
    try {
      if (mode === 'register') await register({ full_name: fullName, email, phone, password });
      else await login(username, password);
      onLogin();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Не удалось выполнить действие');
    } finally {
      setBusy(false);
    }
  }

  return <div className="login-wrap"><form className="panel login" onSubmit={submit}>
    <div className="eyebrow">Личный кабинет предпринимателя</div>
    <h1>{mode === 'login' ? 'Войти в кабинет' : 'Создать личный кабинет'}</h1>
    <p className="muted">Сначала регистрируется человек. Данные компании понадобятся только при оформлении заявки.</p>
    <div className="auth-tabs">
      <button type="button" className={mode === 'login' ? '' : 'secondary'} onClick={() => { setMode('login'); setError(''); }}>Вход</button>
      <button type="button" className={mode === 'register' ? '' : 'secondary'} onClick={() => { setMode('register'); setError(''); }}>Регистрация</button>
    </div>
    {mode === 'register' ? <>
      <label>ФИО<input autoComplete="name" value={fullName} onChange={e => setFullName(e.target.value)} placeholder="Иван Иванович Иванов" required minLength={3} /></label>
      <label>Email<input type="email" autoComplete="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="ivan@example.ru" required /></label>
      <label>Телефон<input type="tel" autoComplete="tel" value={phone} onChange={e => setPhone(e.target.value)} placeholder="+7 900 000-00-00" required minLength={5} /></label>
      <label>Пароль<input type="password" autoComplete="new-password" value={password} onChange={e => setPassword(e.target.value)} required minLength={8} /></label>
    </> : <>
      <label>Email или логин<input autoComplete="username" value={username} onChange={e => setUsername(e.target.value)} required /></label>
      <label>Пароль<input type="password" autoComplete="current-password" value={password} onChange={e => setPassword(e.target.value)} required /></label>
    </>}
    {error && <p className="error">{error}</p>}
    <button disabled={busy}>{busy ? 'Подождите…' : mode === 'login' ? 'Войти' : 'Зарегистрироваться'}</button>
  </form></div>;
}
