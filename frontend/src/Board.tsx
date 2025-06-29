import { useEffect, useRef } from 'react';
import { Chess } from 'chess.js';
import { Chessground } from 'chessground';
import 'chessground/assets/chessground.css';

interface Props {
  fen: string;
  onMove: (uci: string) => void;
}

export default function Board({ fen, onMove }: Props) {
  const divRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!divRef.current) return;
    const chess = new Chess(fen);
    const cg = Chessground(divRef.current, {
      fen,
      movable: {
        free: false,
        color: chess.turn() === 'w' ? 'white' : 'black',
        dests: Object.fromEntries(
          chess.SQUARES.map((sq: any) => [sq, chess.moves({ square: sq, verbose: true }).map((m: any) => m.to)])
        ),
        events: {
          after: (orig: string, dest: string) => onMove(orig + dest),
        },
      },
    });
    return () => cg.destroy();
  }, [fen, onMove]);

  return <div ref={divRef} style={{ width: 480, height: 480 }} />;
} 