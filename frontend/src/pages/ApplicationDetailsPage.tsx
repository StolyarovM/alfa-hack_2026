
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getApplication, type Application } from '../api/applications';
import { money, dateTime } from '../lib/formatters';

function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    SUBMITTED: 'Заявка принята',
    DATA_CHECK: 'Проверяем данные компании',
    EXTERNAL_CHECKS: 'Выполняем проверки',
    SCORING: 'Оцениваем заявку',
    RESULT_READY: 'Результат получен',
    CHECK_ERROR: 'Ошибка проверки данных',
    SCORING_ERROR: 'Не удалось обработать заявку',
  };

  return labels[status] || 'Заявка обрабатывается';
}

function getDecision(outcome: string | null | undefined, status: string) {
  const value = (outcome || '').toLowerCase();

  if (value.includes('отказ')) {
    return {
      title: 'В кредите отказано',
      description: 'По результатам оценки заявка получила отказ.',
      type: 'rejected',
    };
  }

  if (
    value.includes('одобр') ||
    value.includes('приемлемый риск')
  ) {
    return {
      title: 'Кредит предварительно одобрен',
      description: 'Скоринговая модель вернула положительное решение.',
      type: 'approved',
    };
  }

  if (
    value.includes('дополнительн') ||
    value.includes('других условиях')
  ) {
    return {
      title: 'Требуется дополнительное рассмотрение',
      description:
        'Рекомендуется уточнить данные или рассмотреть другие условия финансирования.',
      type: 'review',
    };
  }

  if (status === 'SCORING_ERROR' || status === 'CHECK_ERROR') {
    return {
      title: 'Не удалось получить результат',
      description:
        'При обработке заявки произошла ошибка. Попробуйте позже.',
      type: 'review',
    };
  }

  if (status === 'RESULT_READY') {
    return {
      title: 'Результат оценки получен',
      description:
        'Обработка завершена, но решение не удалось определить однозначно.',
      type: 'review',
    };
  }

  return {
    title: 'Заявка находится на рассмотрении',
    description:
      'Дождитесь завершения проверок. Результат появится на этой странице.',
    type: 'review',
  };
}

export default function ApplicationDetailsPage() {
  const { id = '' } = useParams();
  const [item, setItem] = useState<Application | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    setItem(null);
    setError('');

    getApplication(id)
      .then(setItem)
      .catch((e) => setError(e.message));
  }, [id]);

  const decision = item
    ? getDecision(item.outcome, item.status)
    : null;

  return (
    <>
      <Link to="/" className="back">
        ← В кабинет
      </Link>

      <div className="eyebrow">Результат рассмотрения</div>
      <h1>Заявка №{id}</h1>

      {error && <p className="error">{error}</p>}

      {!item ? (
        !error && <p>Загружаем данные…</p>
      ) : (
        <>
          <div className="panel">
            <div className="section-head">
              <div>
                <h2>{item.product_type}</h2>
                <p className="muted">{dateTime(item.created_at)}</p>
              </div>

              <span className="pill">
                {getStatusLabel(item.status)}
              </span>
            </div>

            <div className={`decision-result ${decision?.type}`}>
              <h2>{decision?.title}</h2>
              <p>{decision?.description}</p>
            </div>

            <p className="muted">Запрошенная сумма кредита</p>
            <h2>{money(item.requested_amount)}</h2>

            {item.risk !== null && item.risk !== undefined && (
              <p>
                Оценка риска отказа:{' '}
                <strong>{(item.risk * 100).toFixed(0)}%</strong>
              </p>
            )}

            {item.scoring_reason && (
              <div className="notice">
                <strong>Причина отказа:</strong> {item.scoring_reason}
              </div>
            )}

            {item.conditions && (
              <div className="notice">
                <strong>Возможные условия:</strong> {item.conditions}
              </div>
            )}
          </div>

          <div className="panel">
            <h2>Этапы проверки</h2>

            {(item.checks || []).length === 0 ? (
              <p className="muted">
                Информация о проверках пока отсутствует.
              </p>
            ) : (
              <ol className="tracker">
                {(item.checks || []).map((check, index) => (
                  <li key={index}>
                    <span
                      className={`dot ${check.status.toLowerCase()}`}
                    />
                    <div>
                      <strong>{check.name}</strong>
                      <p className="muted">
                        {check.message || check.status}
                      </p>
                    </div>
                    <span className="pill">{check.status}</span>
                  </li>
                ))}
              </ol>
            )}
          </div>
        </>
      )}
    </>
  );
}
