import { useState, useEffect } from 'react';

interface Position {
  id: number;
  name: string;
  category: string;
  icon: string;
  fen: string;
}

export default function Menu({ onPick }: { onPick: (pos: Position) => void }) {
  const [positions, setPositions] = useState<Position[]>([]);
  const [cat, setCat] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/positions')
      .then(r => r.json())
      .then(setPositions);
  }, []);

  const categoryObjs = Array.from(
    new Map(positions.map(p => [p.category, p.icon])).entries()
  ).map(([name, icon]) => ({ name, icon }));

  if (!cat) {
    return (
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 20, padding: 20 }}>
        {categoryObjs.map(c => (
          <button
            key={c.name}
            onClick={() => setCat(c.name)}
            style={{
              width: 140,
              height: 160,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              border: '1px solid grey',
              borderRadius: 8,
              background: '#1e1e1e',
              color: 'white',
              cursor: 'pointer',
            }}
          >
            <img src={`/${c.icon}`} alt={c.name} style={{ width: 100, height: 100 }} />
            <span>{c.name}</span>
          </button>
        ))}
      </div>
    );
  }

  const list = positions.filter(p => p.category === cat);

  return (
    <div style={{ padding: 20 }}>
      <button onClick={() => setCat(null)} style={{ marginBottom: 10 }}>
        ← Back
      </button>
      <h3>{cat}</h3>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {list.map(p => (
          <li key={p.id} style={{ margin: '6px 0' }}>
            <button onClick={() => onPick(p)}>{p.name}</button>
          </li>
        ))}
      </ul>
    </div>
  );
} 