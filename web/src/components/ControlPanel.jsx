import { useState } from 'react';

const SAMPLE_MESSAGES = ['Bonjour, monde !', 'ADN vs SILICIUM', 'Projet S9', 'ATCG-2024'];

export default function ControlPanel({ onRun, loading }) {
  const [message, setMessage] = useState('Bonjour, monde !');
  const [errorRate, setErrorRate] = useState(0.05);
  const [useProtection, setUseProtection] = useState(true);
  const [seed, setSeed] = useState('');

  const canRun = message.trim().length > 0 && !loading;

  const submit = (event) => {
    event.preventDefault();
    if (canRun) {
      onRun({
        message: message.trim(),
        errorRate,
        useProtection,
        seed: seed.trim(),
      });
    }
  };

  return (
    <form className="card control-panel" onSubmit={submit}>
      <div className="control-row">
        <label className="field field-message">
          <span className="field-label">Message à transmettre (max 64 caractères)</span>
          <textarea
            value={message}
            maxLength={64}
            rows={2}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Saisir le message..."
          />
          <span className="message-samples">
            Exemples :
            {SAMPLE_MESSAGES.map((sample) => (
              <button key={sample} type="button" className="sample-btn" onClick={() => setMessage(sample)}>
                {sample}
              </button>
            ))}
          </span>
        </label>
      </div>

      <div className="control-row controls-inline">
        <label className="field field-slider">
          <span className="field-label">
            Taux d'erreur du canal : <strong>{Math.round(errorRate * 100)} %</strong>
          </span>
          <input
            type="range"
            min="0"
            max="0.3"
            step="0.01"
            value={errorRate}
            onChange={(e) => setErrorRate(Number(e.target.value))}
          />
        </label>

        <label className="field field-check">
          <input
            type="checkbox"
            checked={useProtection}
            onChange={(e) => setUseProtection(e.target.checked)}
          />
          <span>Protection par réplication ×3 (correction d'erreurs)</span>
        </label>

        <label className="field field-seed">
          <span className="field-label">Graine aléatoire (reproductibilité)</span>
          <input
            type="number"
            value={seed}
            placeholder="aléatoire"
            onChange={(e) => setSeed(e.target.value)}
          />
        </label>

        <button type="submit" className="btn-primary" disabled={!canRun}>
          {loading ? 'Transmission en cours...' : 'Lancer la transmission'}
        </button>
      </div>
    </form>
  );
}
