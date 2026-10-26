
export default function PreviousChecks({ checks }: { checks: {name:string;status:string}[] }) { return <section className="panel"><h2>Предыдущие проверки</h2>{checks.length ? checks.map(c => <p key={c.name}>{c.name}: {c.status}</p>) : <p>Проверок пока нет</p>}</section>; }
