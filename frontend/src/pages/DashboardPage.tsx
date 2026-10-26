import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getApplications, type Application } from '../api/applications';
import { getProfile, type Profile } from '../api/profile';
import { money, dateTime } from '../lib/formatters';

export default function DashboardPage() {
  const [profile, setProfile] = useState<Profile | null>(null); const [apps, setApps] = useState<Application[]>([]); const [error, setError] = useState('');
  useEffect(() => { Promise.all([getProfile(), getApplications()]).then(([p,a])=>{setProfile(p);setApps(a)}).catch(e=>setError(e.message)); }, []);
  const firstName = profile?.full_name?.trim().split(/\s+/)[1] || profile?.full_name?.trim().split(/\s+/)[0] || '';
  return <>
    <section className="welcome-banner"><div><div className="eyebrow">Личный кабинет</div><h1>Добро пожаловать{firstName ? `, ${firstName}` : ''}!</h1><p>Подберите финансирование для своих бизнес-задач и отслеживайте заявки в одном месте.</p><Link className="button-link" to="/survey">Подобрать кредит</Link></div><div className="welcome-art" aria-hidden="true">₽</div></section>
    {error && <p className="error">{error}</p>}
    <section className="grid two">
      <div className="panel"><div className="section-head"><h2>Мой профиль</h2><span className="pill">Пользователь</span></div>{profile ? <><p><span className="muted">ФИО</span><strong>{profile.full_name}</strong></p><p><span className="muted">Email</span><strong>{profile.email || 'Не указан'}</strong></p><p><span className="muted">Телефон</span><strong>{profile.phone || 'Не указан'}</strong></p></> : <p>Загружаем профиль…</p>}</div>
      <div className="panel accent"><div className="eyebrow">Ваш следующий шаг</div><h2>Найдём подходящий кредит</h2><p>Ответьте на несколько коротких вопросов. Данные компании запрашиваются только при заполнении заявки.</p><Link to="/survey">Начать подбор →</Link></div>
    </section>
    <section className="news-section"><div className="section-head"><div><div className="eyebrow">Полезное</div><h2>Новости и предложения</h2></div></div><div className="grid three">
      <article className="news-card news-red"><span className="news-label">Финансирование</span><h3>Оборотный кредит для развития бизнеса</h3><p>Рассмотрите финансирование закупок, сезонных расходов и текущих платежей.</p><Link to="/survey">Подобрать продукт →</Link></article>
      <article className="news-card"><span className="news-label">Подготовка</span><h3>Подготовьте данные заранее</h3><p>Для предварительной оценки понадобятся ИНН, выручка и информация о кредитных платежах.</p><Link to="/survey">Начать →</Link></article>
      <article className="news-card"><span className="news-label">Личный кабинет</span><h3>Все заявки в одном месте</h3><p>После отправки заявки здесь можно посмотреть статус проверок и результат оценки.</p><a href="#applications">Мои заявки ↓</a></article>
    </div></section>
    <section className="panel" id="applications"><div className="section-head"><h2>Мои заявки</h2><span className="pill">{apps.length}</span></div>{apps.length ? <div className="app-list">{apps.map(a=><Link className="app-row" to={`/applications/${a.id}`} key={a.id}><div><strong>{a.product_type}</strong><small>{dateTime(a.created_at)}</small></div><div className="right"><strong>{money(a.requested_amount)}</strong><small>{a.outcome || a.status}</small></div></Link>)}</div>:<p className="muted">Пока заявок нет. Вы можете начать с подбора кредита — данные бизнеса понадобятся позже.</p>}</section>
  </>;
}
