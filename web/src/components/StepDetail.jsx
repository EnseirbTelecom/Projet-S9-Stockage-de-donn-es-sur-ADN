import { StepData, DataLegend } from './DataViews';

const KIND_LABELS = {
  text: 'Texte',
  bits: 'Bits',
  dna: 'Séquence ADN',
};

function indexList(items, key = 'index') {
  return new Set(items.map((item) => item[key]));
}

function ErrorTable({ items, columns, emptyText }) {
  if (!items || items.length === 0) {
    return <p className="empty-note">{emptyText}</p>;
  }

  return (
    <table className="detail-table">
      <thead>
        <tr>
          {columns.map((col) => (
            <th key={col.key}>{col.label}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {items.map((item, i) => (
          <tr key={i}>
            {columns.map((col) => (
              <td key={col.key}>{col.format(item)}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default function StepDetail({ step }) {
  const isChannel = step.id === 'channel';
  const isRestore = step.id === 'restore';

  const outputMarked =
    isChannel ? indexList(step.errors || []) : new Set();
  const inputMarked =
    isRestore ? indexList(step.corrections || []) : new Set();

  const positionsOf = (items) =>
    items.map((e) => e.index + 1).join(', ');

  const sameData = step.input === step.output;

  return (
    <section className="card step-detail">
      <header className="step-detail-header">
        <div>
          <h2>Étape {step.label}</h2>
          <p className="step-description">{step.description}</p>
        </div>
        <div className="step-badges">
          {step.strategy && <span className="badge">{step.strategy}</span>}
          {isChannel && (
            <span className={`badge ${step.errors.length > 0 ? 'badge-error' : 'badge-ok'}`}>
              {step.errors.length} erreur{step.errors.length > 1 ? 's' : ''} injectée{step.errors.length > 1 ? 's' : ''}
            </span>
          )}
          {isRestore && (
            <span className={`badge ${step.corrections.length > 0 ? 'badge-ok' : 'badge-neutral'}`}>
              {step.corrections.length} base{step.corrections.length > 1 ? 's' : ''} corrigée{step.corrections.length > 1 ? 's' : ''}
            </span>
          )}
        </div>
      </header>

      <div className={`step-data-grid ${sameData ? 'single' : ''}`}>
        <div className="data-panel">
          <h3>
            Données d'entrée <span className="data-kind">({KIND_LABELS[step.input_kind || step.kind]})</span>
          </h3>
          <StepData
            kind={step.input_kind || step.kind}
            value={step.input}
            markedIndices={inputMarked}
            markType="corrected"
          />
          <DataLegend kind={step.input_kind || step.kind} />
        </div>

        {!sameData && (
          <div className="data-panel">
            <h3>
              Données de sortie <span className="data-kind">({KIND_LABELS[step.output_kind || step.kind]})</span>
            </h3>
            <StepData
              kind={step.output_kind || step.kind}
              value={step.output}
              markedIndices={outputMarked}
              markType="error"
            />
          </div>
        )}
      </div>

      {isChannel && step.errors.length > 0 && (
        <div className="event-section">
          <h4>Substitutions introduites par le canal</h4>
          <ErrorTable
            items={step.errors}
            columns={[
              { key: 'pos', label: 'Position', format: (e) => e.index + 1 },
              { key: 'original', label: 'Base émise', format: (e) => e.original },
              { key: 'received', label: 'Base reçue', format: (e) => e.received },
            ]}
            emptyText="Le canal n'a introduit aucune erreur : la séquence transmise est identique à la séquence émise."
          />
        </div>
      )}

      {isRestore && (
        <div className="event-section">
          <h4>Corrections appliquées par vote majoritaire</h4>
          {step.corrections.length > 0 ? (
            <ErrorTable
              items={step.corrections}
              columns={[
                { key: 'block', label: 'Bloc', format: (e) => e.block + 1 },
                { key: 'pos', label: 'Position', format: (e) => e.index + 1 },
                { key: 'received', label: 'Base reçue', format: (e) => e.received },
                { key: 'corrected', label: 'Base restaurée', format: (e) => e.corrected },
              ]}
            />
          ) : (
            <p className="empty-note">
              Aucune correction nécessaire : chaque triplet répété était complet et cohérent.
            </p>
          )}
        </div>
      )}

      {isChannel && step.errors.length > 0 && (
        <p className="position-note">Positions concernées : {positionsOf(step.errors)}</p>
      )}
    </section>
  );
}
