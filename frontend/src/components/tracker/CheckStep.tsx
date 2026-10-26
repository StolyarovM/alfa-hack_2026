
export default function CheckStep({ name, status }: { name: string; status: string }) { return <li><strong>{name}</strong> <span className="pill">{status}</span></li>; }
