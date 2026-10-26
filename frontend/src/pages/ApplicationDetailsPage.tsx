import { useEffect, useState, type FormEvent } from 'react';
import { Link, useParams } from 'react-router-dom';

import {
  getApplication,
  chatWithApplication,
  type Application,
} from '../api/applications';

import { money, dateTime } from '../lib/formatters';

type ChatMessage = {
  role: 'user' | 'assistant';
  text: string;
};

export default function ApplicationDetailsPage() {
  const { id = '' } = useParams();

  const [item, setItem] = useState<Application | null>(null);
  const [error, setError] = useState('');

  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      text:
        'Здравствуйте! Я ИИ-ассистент кредитного кабинета. ' +
        'Могу объяснить статус заявки и помочь разобраться ' +
        'в доступной информации о результате проверки.',
    },
  ]);

  const [sending, setSending] = useState(false);
  const [chatError, setChatError] = useState('');

  useEffect(() => {
    let active = true;

    getApplication(id)
      .then((application) => {
        if (active) {
          setItem(application);
          setError('');
        }
      })
      .catch((e: Error) => {
        if (active) {
          setError(e.message || 'Не удалось загрузить заявку');
        }
      });

    return () => {
      active = false;
    };
  }, [id]);

  async function sendMessage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const text = question.trim();

    if (!text || sending || !item) {
      return;
    }

    setQuestion('');
    setChatError('');

    setMessages((current) => [
      ...current,
      {
        role: 'user',
        text,
      },
    ]);

    setSending(true);

    try {
      const result = await chatWithApplication(id, text);

      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          text: result.reply,
        },
      ]);
    } catch (e) {
      setChatError(
        e instanceof Error
          ? e.message
          : 'Не удалось получить ответ ИИ-ассистента.',
      );
    } finally {
      setSending(false);
    }
  }

  return (
    <>
      <Link to="/" className="back">
        ← В кабинет
      </Link>

      <div className="eyebrow">Статус заявки</div>
      <h1>Заявка №{id}</h1>

      {error && <p className="error">{error}</p>}

      {!item ? (
        !error && <p>Загружаем данные…</p>
      ) : (
        <>
          <section className="panel">
            <div className="section-head">
              <div>
                <h2>{item.product_type}</h2>
                <p className="muted">
                  {dateTime(item.created_at)}
                </p>
              </div>

              <span className="pill">
                {item.outcome || item.status}
              </span>
            </div>

            <h2>{money(item.requested_amount)}</h2>

            {item.risk !== null && item.risk !== undefined && (
              <p>
                Оценка риска демонстрационной модели:{' '}
                {(item.risk * 100).toFixed(0)}%
              </p>
            )}
          </section>

          <section className="panel">
            <h2>Этапы проверки</h2>

            <ol className="tracker">
              {(item.checks || []).map((check, index) => (
                <li key={`${check.name}-${index}`}>
                  <span
                    className={`dot ${check.status.toLowerCase()}`}
                  />

                  <div>
                    <strong>{check.name}</strong>
                    <p className="muted">
                      {check.message || check.status}
                    </p>
                  </div>

                  <span className="pill">
                    {check.status}
                  </span>
                </li>
              ))}
            </ol>

            <p className="muted">
              Результат является демонстрационным и не является
              офертой или окончательным решением банка.
            </p>
          </section>

          <section className="panel">
            <h2>ИИ-ассистент</h2>

            <p className="muted">
              Задайте вопрос о своей заявке. Ассистент использует
              результат проверки и модель Qwen через Ollama.
            </p>

            <div
              role="log"
              aria-live="polite"
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: 12,
                marginTop: 20,
                marginBottom: 20,
              }}
            >
              {messages.map((message, index) => (
                <div
                  key={`${message.role}-${index}`}
                  style={{
                    alignSelf:
                      message.role === 'user'
                        ? 'flex-end'
                        : 'flex-start',
                    maxWidth: '85%',
                    padding: 12,
                    borderRadius: 12,
                    background:
                      message.role === 'user'
                        ? '#eef2f7'
                        : '#f6f6f6',
                    overflowWrap: 'anywhere',
                    whiteSpace: 'pre-wrap',
                  }}
                >
                  <strong>
                    {message.role === 'user'
                      ? 'Вы'
                      : 'ИИ-ассистент'}
                  </strong>

                  <p style={{ marginBottom: 0 }}>
                    {message.text}
                  </p>
                </div>
              ))}
            </div>

            {chatError && (
              <p className="error" role="alert">
                {chatError}
              </p>
            )}

            <form
              onSubmit={sendMessage}
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: 12,
              }}
            >
              <textarea
                value={question}
                onChange={(event) =>
                  setQuestion(event.target.value)
                }
                placeholder="Например: объясни статус моей заявки"
                maxLength={2000}
                rows={3}
                disabled={sending}
                required
                style={{
                  boxSizing: 'border-box',
                  width: '100%',
                  resize: 'vertical',
                }}
              />

              <button
                type="submit"
                disabled={
                  sending || !question.trim() || !item
                }
              >
                {sending
                  ? 'Модель готовит ответ…'
                  : 'Отправить вопрос'}
              </button>
            </form>

            <p className="muted">
              Ответы генерируются искусственным интеллектом и
              могут содержать ошибки. Не отправляйте пароли,
              платёжные реквизиты и другие секретные данные.
            </p>
          </section>
        </>
      )}
    </>
  );
}