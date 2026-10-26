
import type { Application } from '../../api/applications';
import { Link } from 'react-router-dom';
export default function ApplicationsList({ applications }: { applications: Application[] }) { return <section className="panel"><h2>Заявки</h2>{applications.map(a => <p key={a.id}><Link to={`/applications/${a.id}`}>Заявка №{a.id} — {a.status}</Link></p>)}</section>; }
