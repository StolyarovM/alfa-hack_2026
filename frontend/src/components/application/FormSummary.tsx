
import { money } from '../../lib/formatters';
export default function FormSummary({ product, amount }: { product: string; amount: number }) { return <aside className="panel"><strong>{product}</strong><h2>{money(amount)}</h2></aside>; }
