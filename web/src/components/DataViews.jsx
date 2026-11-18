const BASE_CLASS = { A: 'base-a', T: 'base-t', C: 'base-c', G: 'base-g' };

const MAX_TILES = 1200;

export function TextBlock({ value }) {
  return <div className="text-block">{value}</div>;
}

export function BitsBlock({ value }) {
  const bytes = [];
  for (let i = 0; i < value.length; i += 8) {
    bytes.push(value.slice(i, i + 8));
  }

  return (
    <div className="bits-block">
      {bytes.map((byte, i) => (
        <span className="byte" key={i}>
          {byte.split('').map((bit, j) => (
            <span key={j} className={`bit bit-${bit}`}>{bit}</span>
          ))}
        </span>
      ))}
    </div>
  );
}

export function DnaBlock({ value, markedIndices = new Set(), markType = 'error' }) {
  const tiles = [];
  const limit = Math.min(value.length, MAX_TILES);

  for (let i = 0; i < limit; i++) {
    const base = value[i];
    const classes = ['dna-tile', BASE_CLASS[base] || ''];
    if (markedIndices.has(i)) classes.push(markType === 'error' ? 'tile-error' : 'tile-corrected');
    tiles.push(
      <span key={i} className={classes.join(' ')} title={`Position ${i + 1}`}>
        {base}
      </span>
    );
  }

  return (
    <div className="dna-block">
      {tiles}
      {value.length > MAX_TILES && (
        <p className="dna-truncated">
          Affichage limité aux {MAX_TILES} premières bases sur {value.length}.
        </p>
      )}
    </div>
  );
}

export function StepData({ kind, value, markedIndices, markType }) {
  if (kind === 'bits') return <BitsBlock value={value} />;
  if (kind === 'dna') return <DnaBlock value={value} markedIndices={markedIndices} markType={markType} />;
  return <TextBlock value={value} />;
}

export function DataLegend({ kind }) {
  if (kind === 'dna') {
    return (
      <div className="legend">
        <span><span className="legend-swatch base-a">A</span> Adénine (bit 0)</span>
        <span><span className="legend-swatch base-t">T</span> Thymine (bit 0)</span>
        <span><span className="legend-swatch base-c">C</span> Cytosine (bit 1)</span>
        <span><span className="legend-swatch base-g">G</span> Guanine (bit 1)</span>
        <span><span className="legend-swatch tile-error">E</span> Erreur injectée</span>
        <span><span className="legend-swatch tile-corrected">C</span> Base corrigée</span>
      </div>
    );
  }
  if (kind === 'bits') {
    return (
      <div className="legend">
        <span><span className="legend-swatch bit bit-0">0</span> Bit 0</span>
        <span><span className="legend-swatch bit bit-1">1</span> Bit 1</span>
        <span>Blocs de 8 bits = 1 caractère UTF-8</span>
      </div>
    );
  }
  return null;
}
