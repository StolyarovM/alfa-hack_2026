
export default function ProfileCard({ inn, name }: { inn: string; name: string }) { return <section className="panel"><h2>{name}</h2><p>ИНН: {inn}</p></section>; }
