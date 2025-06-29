import { useEffect, useRef } from 'react';
import { Chess, SQUARES } from 'chess.js';
import { Chessground } from 'chessground';
import "chessground/assets/chessground.base.css";
import "chessground/assets/chessground.cburnett.css";  // pick a theme you like

interface Props {
  fen: string;
  onMove: (uci: string) => void;
}

export default function Board({ fen, onMove }: Props) {
  const divRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!divRef.current) return;
    const chess = new Chess(fen);
    // Build dests Map <square, string[]> for chessground v9
    const dests = new Map<any, string[]>();
    SQUARES.forEach((sq: string) => {
      const targets = chess.moves({ square: sq, verbose: true }).map((m: any) => m.to);
      if (targets.length) dests.set(sq, targets);
    });

    const cg = Chessground(divRef.current, {
      fen,
      movable: {
        free: false,
        color: chess.turn() === 'w' ? 'white' : 'black',
        dests,
        events: {
          after: (orig: string, dest: string) => onMove(orig + dest),
        },
      },
    });
    return () => cg.destroy();
  }, [fen, onMove]);

  return <div ref={divRef} style={{ width: 480, height: 480 }} />;
} 