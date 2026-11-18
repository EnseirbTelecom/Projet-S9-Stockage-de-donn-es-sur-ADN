import { useEffect, useState } from 'react';

const SAMPLE_MESSAGES = ['Bonjour, monde !', 'ADN vs SILICIUM', 'Projet S9', 'ATCG-2024'];

const NONE_PROTECTION = 'none';

function StrategySelect({ label, items, value, onChange }) {
  if (!items || items.length === 0) return null;

  return (
    <label className="field field-strategy">
      <span className="field-label">{label}</span>
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        {items.map((item) => (
          <option
            key={item.slug}
            value={item.slug}
            title={item.description}
          >
            {item.name}
          </option>
        ))}
      </select>
    </label>
  );
}

export default function ControlPanel({ catalog, onRun, loading }) {
  const [message, setMessage] = useState('Bonjour, monde !');
  const [errorRate, setErrorRate] = useState(0.05);
  const [protection, setProtection] = useState('');
  const [seed, setSeed] = useState('');
  const [encoder, setEncoder] = useState('');
  const [decoder, setDecoder] = useState('');
  const [channel, setChannel] = useState('');

  // Sélection par défaut : première implémentation du catalogue
  useEffect(() => {
    if (!catalog) return;
    setEncoder((v) => v || catalog.encoder?.[0]?.slug || '');
    setDecoder((v) => v || catalog.decoder?.[0]?.slug || '');
    setChannel((v) => v || catalog.channel?.[0]?.slug || '');
    setProtection((v) => v || catalog.protection?.[0]?.slug || NONE_PROTECTION);
  }, [catalog]);

  const protectionEnabled = protection !== '' && protection !== NONE_PROTECTION;
  const canRun = message.trim().length > 0 && !loading;

  const submit = (event) => {
    event.preventDefault();
    if (canRun) {
      onRun({
        message: message.trim(),
        errorRate,
        useProtection: protectionEnabled,
        seed: seed.trim(),
        encoder,
        decoder,
        channel,
        protection: protectionEnabled ? protection : undefined,
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
        <StrategySelect
          label="Encodeur"
          items={catalog?.encoder}
          value={encoder}
          onChange={setEncoder}
        />
        <StrategySelect
          label="Décodeur"
          items={catalog?.decoder}
          value={decoder}
          onChange={setDecoder}
        />
        <StrategySelect
          label="Canal de transmission"
          items={catalog?.channel}
          value={channel}
          onChange={setChannel}
        />
        <label className="field field-strategy">
          <span className="field-label">Protection</span>
          <select
            value={protection}
            onChange={(e) => setProtection(e.target.value)}
            disabled={!catalog?.protection?.length}
          >
            <option value={NONE_PROTECTION}>Aucune protection</option>
            {catalog?.protection?.map((item) => (
              <option
                key={item.slug}
                value={item.slug}
                title={item.description}
              >
                {item.name}
              </option>
            ))}
          </select>
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
