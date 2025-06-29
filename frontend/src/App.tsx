import { useState } from 'react'
import Board from './Board'
import Menu from './Menu'
import './App.css'

function App() {
  const [fen, setFen] = useState<string | null>(null)

  if (!fen) return <Menu onPick={p => setFen(p.fen)} />

  return (
    <Board
      fen={fen}
      onMove={uci =>
        fetch('/api/move', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ fen, move: uci }),
        })
          .then(r => r.json())
          .then(d => d.ok && setFen(d.fen))
      }
    />
  )
}

export default App
