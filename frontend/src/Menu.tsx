import { useState, useEffect } from 'react';

interface Position { id: number; name: string; category: string; fen: string }

export default function Menu({ onPick }: { onPick: (pos: Position) => void }) {
  const [positions, setPositions] = useState<Position[]>([]);
  const [cat, setCat] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/positions').then(r => r.json()).then(setPositions);
  }, []);

  const categories = Array.from(new Set(positions.map(p => p.category)));

  if (!cat) {
    return (
      <div>
        <h2>Pick a category</h2>
        {categories.map(c => (
          <button key={c} onClick={() => setCat(c)} style={{ margin: 6 }}>
            {c}
          </button>
        ))}
      </div>
    );
  }

  const list = positions.filter(p => p.category === cat);

  return (
    <div>
      <button onClick={() => setCat(null)}>← back</button>
      <h3>{cat}</h3>
      <ul>
        {list.map(p => (
          <li key={p.id}>
            <button onClick={() => onPick(p)}>{p.name}</button>
          </li>
        ))}
      </ul>
    </div>
  );
} 