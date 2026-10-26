
import { Link, Navigate, Route, Routes } from 'react-router-dom';
import { useEffect, useState } from 'react';
import LoginPage from '../pages/LoginPage';
import DashboardPage from '../pages/DashboardPage';
import NeedsSurveyPage from '../pages/NeedsSurveyPage';
import LoanApplicationPage from '../pages/LoanApplicationPage';
import ApplicationDetailsPage from '../pages/ApplicationDetailsPage';
import { logout, tokenExists } from '../api/auth';

export default function App() {
  const [signedIn, setSignedIn] = useState(tokenExists());
  useEffect(() => {
    const onUnauthorized = () => setSignedIn(false);
    window.addEventListener('credit:unauthorized', onUnauthorized);
    return () => window.removeEventListener('credit:unauthorized', onUnauthorized);
  }, []);
  if (!signedIn) return <Routes><Route path="/login" element={<LoginPage onLogin={() => setSignedIn(true)} />} /><Route path="*" element={<Navigate to="/login" replace />} /></Routes>;
  return <div className="shell">
    <header className="topbar"><Link to="/" className="brand">Альфа • Кредитный кабинет</Link><nav><Link to="/">Главная</Link><Link to="/survey">Подбор кредита</Link><button className="secondary" onClick={() => { logout(); setSignedIn(false); }}>Выйти</button></nav></header>
    <main className="content"><Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/survey" element={<NeedsSurveyPage />} />
      <Route path="/application/new" element={<LoanApplicationPage />} />
      <Route path="/applications/:id" element={<ApplicationDetailsPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes></main>
    <footer>Личный кабинет предпринимателя</footer>
  </div>;
}
