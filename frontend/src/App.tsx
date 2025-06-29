import { useState } from 'react'
import Board from './Board'
import Menu from './Menu'
import './App.css'
import { Chess } from 'chess.js'

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
          .then(d => {
            if (!d.ok) return;
            setFen(d.fen);
            const ch = new Chess(d.fen);
            if (ch.isGameOver()) {
              const message = ch.isCheckmate()
                ? `Checkmate – ${ch.turn() === 'w' ? 'Black' : 'White'} wins!`
                : 'Draw!';
              alert(message);
              setFen(null);
            }
          })
      }
    />
  )
}

export default App
