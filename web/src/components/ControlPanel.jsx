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
  const [channelParameters, setChannelParameters] = useState({});
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

  const selectedChannel = catalog?.channel?.find((item) => item.slug === channel);

  useEffect(() => {
    if (!selectedChannel) return;
    const defaults = Object.fromEntries(
      Object.entries(selectedChannel.parameters ?? {})
        .filter(([name]) => name !== 'seed')
        .map(([name, parameter]) => [name, parameter.default ?? 0]),
    );
    setChannelParameters(defaults);
  }, [selectedChannel]);

  const protectionEnabled = protection !== '' && protection !== NONE_PROTECTION;
  const probabilityTotal = ['pts', 'pi', 'pd'].reduce(
    (total, name) => total + (channelParameters[name] ?? 0),
    0,
  );
  const validChannelParameters = probabilityTotal <= 1;
  const canRun = message.trim().length > 0 && !loading && validChannelParameters;

  const submit = (event) => {
    event.preventDefault();
    if (canRun) {
      onRun({
        message: message.trim(),
        useProtection: protectionEnabled,
        seed: seed.trim(),
        encoder,
        decoder,
        channel,
        channelParameters,
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
          label="Conversion : Binaire -> ADN"
          items={catalog?.encoder}
          value={encoder}
          onChange={setEncoder}
        />
        <StrategySelect
          label="Conversion : ADN -> Binaire"
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
        {Object.entries(selectedChannel?.parameters ?? {})
          .filter(([name]) => name !== 'seed')
          .map(([name, parameter]) => (
            <label className="field field-parameter" key={name}>
              <span className="field-label">{parameter.label ?? name}</span>
              <input
                type="number"
                min={parameter.min}
                max={parameter.max}
                step={parameter.type === 'integer' ? 1 : 0.01}
                value={channelParameters[name] ?? parameter.default ?? ''}
                onChange={(event) => setChannelParameters((current) => ({
                  ...current,
                  [name]: Number(event.target.value),
                }))}
              />
            </label>
          ))}

        {!validChannelParameters && (
          <span className="field-validation" role="alert">
            La somme de pts, pi et pd ne doit pas dépasser 1.
          </span>
        )}

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
