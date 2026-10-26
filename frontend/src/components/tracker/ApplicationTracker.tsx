
export default function ApplicationTracker({ steps }: { steps: {name:string;status:string}[] }) { return <ol className="tracker">{steps.map(s => <li key={s.name}><span className="dot"></span><strong>{s.name}</strong><span className="pill">{s.status}</span></li>)}</ol>; }
