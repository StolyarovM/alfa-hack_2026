import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { createApplication } from '../api/applications';

type Chosen = { id: string; name: string; type: string; requested_amount: number };
type Scenario = 'approval' | 'decline' | 'conditional' | '';

const scenarios = {
  approval: {
    businessName: 'ИП Иванов Иван Иванович', inn: '7801234567', industry: 'Услуги', age: '35',
    revenue: '800000', payments: '20000', overdue: false, collateral: true, amount: '500000',
  },
  decline: {
    businessName: 'ИП Петров Алексей Сергеевич', inn: '7701234567', industry: 'Онлайн-торговля', age: '30',
    revenue: '300000', payments: '210000', overdue: true, collateral: false, amount: '1000000',
  },
  conditional: {
    businessName: 'ИП Смирнова Мария Андреевна', inn: '7801234567', industry: 'Услуги', age: '38',
    revenue: '500000', payments: '175000', overdue: false, collateral: false, amount: '2500000',
  },
} as const;

export default function LoanApplicationPage() {
  const [businessName, setBusinessName] = useState('');
  const [inn, setInn] = useState('');
  const [industry, setIndustry] = useState('');
  const [age, setAge] = useState('30');
  const [revenue, setRevenue] = useState('500000');
  const [payments, setPayments] = useState('0');
  const [overdue, setOverdue] = useState(false);
  const [collateral, setCollateral] = useState(false);
  const [amount, setAmount] = useState('1000000');
  const [scenario, setScenario] = useState<Scenario>('');
  const [chosen, setChosen] = useState<Chosen | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const raw = sessionStorage.getItem('chosenProduct');
    if (raw) {
      const p = JSON.parse(raw);
      setChosen(p);
      setAmount(String(p.requested_amount || 1000000));
    }
  }, []);

  function applyScenario(value: Scenario) {
    setScenario(value);
    if (!value) return;
    const data = scenarios[value];
    setBusinessName(data.businessName);
    setInn(data.inn);
    setIndustry(data.industry);
    setAge(data.age);
    setRevenue(data.revenue);
    setPayments(data.payments);
    setOverdue(data.overdue);
    setCollateral(data.collateral);
    setAmount(data.amount);
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError('');
    try {
      const result = await createApplication({
        business_name: businessName,
        inn,
        industry,
        age_ip: Number(age),
        monthly_revenue: Number(revenue),
        monthly_credit_payments: Number(payments),
        has_overdue: overdue,
        has_collateral: collateral,
        product_type: chosen?.type || 'Оборотный',
        requested_amount: Number(amount),
      });
      sessionStorage.removeItem('chosenProduct');
      navigate(`/applications/${result.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Не удалось отправить заявку');
    } finally {
      setBusy(false);
    }
  }

  return <div className="company-form-page">
    <Link to="/survey" className="back">← К подбору</Link>
    <section className="company-form-card">
      <div className="company-form-heading">
        <div className="eyebrow">Кредитная заявка</div>
        <h1>Расскажите о бизнесе</h1>
        <p className="muted">Личные данные уже находятся в вашем профиле. Здесь указываются сведения о бизнесе и его финансовом состоянии.</p>
      </div>
      <form className="company-form-grid" onSubmit={submit}>
        <label>Пример заполнения
          <select value={scenario} onChange={e => applyScenario(e.target.value as Scenario)}>
            <option value="">Заполнить вручную</option>
            <option value="approval">Низкая долговая нагрузка — вероятное одобрение</option>
            <option value="decline">Есть просрочки — вероятный отказ</option>
            <option value="conditional">Умеренная нагрузка — оценка на других условиях</option>
          </select>
        </label>
        <p className="muted scenario-hint">Пример подставляет значения в поля. Итог зависит от результата скоринговой модели и проверок.</p>
        <label>Название компании или ИП<input value={businessName} onChange={e => setBusinessName(e.target.value)} placeholder="Например, ИП Иванов Иван Иванович" required minLength={2} /></label>
        <label>ИНН компании / ИП<input inputMode="numeric" value={inn} onChange={e => setInn(e.target.value.replace(/\D/g, '').slice(0, 12))} placeholder="10 или 12 цифр" minLength={10} maxLength={12} required /></label>
        <label>Отрасль<select value={industry} onChange={e => setIndustry(e.target.value)} required><option value="">Выберите отрасль</option><option>Онлайн-торговля</option><option>Розничная торговля</option><option>Оптовая торговля</option><option>Производство</option><option>Строительство</option><option>Услуги</option><option>Транспорт и логистика</option><option>IT и телеком</option><option>Общепит</option><option>Другая отрасль</option></select></label>
        <label>Возраст ИП, лет<input type="number" min="18" max="100" value={age} onChange={e => setAge(e.target.value)} required /></label>
        <label>Выручка в месяц, ₽<input type="number" min="1" value={revenue} onChange={e => setRevenue(e.target.value)} required /></label>
        <label>Платежи по кредитам в месяц, ₽<input type="number" min="0" value={payments} onChange={e => setPayments(e.target.value)} required /></label>
        <label className="check"><input type="checkbox" checked={overdue} onChange={e => setOverdue(e.target.checked)} /> Были просрочки по кредитам</label>
        <label className="check"><input type="checkbox" checked={collateral} onChange={e => setCollateral(e.target.checked)} /> Есть залог</label>
        <label>Кредитный продукт<input value={chosen?.name || 'Оборотный кредит'} readOnly /></label>
        <label>Запрашиваемая сумма, ₽<input type="number" min="10000" value={amount} onChange={e => setAmount(e.target.value)} required /></label>
        {Number(revenue) > 0 && <p className="notice">Долговая нагрузка по введённым данным: {(Number(payments) / Number(revenue) * 100).toFixed(1)}%</p>}
        {error && <p className="error">{error}</p>}
        <button disabled={busy}>{busy ? 'Отправляем…' : 'Отправить заявку'}</button>
      </form>
    </section>
  </div>;
}
