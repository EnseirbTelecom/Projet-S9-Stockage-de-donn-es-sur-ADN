import { useEffect, useState } from 'react';
import { importDnaFile, fetchDnaFiles, dnaFileDownloadUrl } from '../lib/api';
import { DnaBlock } from './DataViews';

function formatBytes(size) {
  if (size < 1024) return `${size} o`;
  return `${(size / 1024).toFixed(1)} Ko`;
}

function formatSizeBases(count) {
  return count.toLocaleString('fr-FR');
}

export default function ImportPanel() {
  const [file, setFile] = useState(null);
  const [seed, setSeed] = useState('');
  const [encoder, setEncoder] = useState('one2one');
  const [protection, setProtection] = useState('');
  const [showDevOptions, setShowDevOptions] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [stored, setStored] = useState([]);
  const [error, setError] = useState(null);

  const refreshStored = () => {
    fetchDnaFiles()
      .then((files) => setStored(files))
      .catch(() => setStored([]));
  };

  useEffect(() => {
    refreshStored();
  }, []);

  const canImport = file && !loading;

  const submit = async (event) => {
    event.preventDefault();
    if (!canImport) return;

    setLoading(true);
    setError(null);
    try {
      const data = await importDnaFile(file, {
        encoder,
        protection,
        seed: seed.trim(),
      });
      setResult(data);
      refreshStored();
    } catch (e) {
      setError(e.message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card import-panel">
      <h2>Stocker un fichier dans l'ADN</h2>
      <p className="import-intro">
        Importez un fichier : son contenu binaire est converti en bits (UTF-8, 8 bits par octet)
        puis encodé en bases azotées par l'API, et la séquence ADN obtenue est enregistrée en base
        de données. Le fichier ADN reste téléchargeable à tout moment.
      </p>

      <form className="import-form" onSubmit={submit}>
        <label className="field field-file">
          <span className="field-label">Fichier à encoder (512 Ko maximum)</span>
          <input
            type="file"
            onChange={(e) => setFile(e.target.files.length > 0 ? e.target.files[0] : null)}
          />
          {file && (
            <span className="file-meta">
              {file.name} — {formatBytes(file.size)}
            </span>
          )}
        </label>

        {showDevOptions ? (
          <div className="dev-options">
            <label className="field">
              <span className="field-label">Encodeur</span>
              <select value={encoder} onChange={(e) => setEncoder(e.target.value)}>
                <option value="one2one">One2One — 1 bit → 1 base</option>
                <option value="gray">Gray — 2 bits → 1 base</option>
              </select>
            </label>

            <label className="field">
              <span className="field-label">Protection</span>
              <select value={protection} onChange={(e) => setProtection(e.target.value)}>
                <option value="">Aucune</option>
                <option value="replication">Réplication ×3</option>
              </select>
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

            <button
              type="button"
              className="dev-toggle"
              onClick={() => setShowDevOptions(false)}
            >
              Masquer les options
            </button>
          </div>
        ) : (
          <button
            type="button"
            className="dev-toggle"
            onClick={() => setShowDevOptions(true)}
          >
            Options développeur
          </button>
        )}

        <button type="submit" className="btn-primary" disabled={!canImport}>
          {loading ? 'Encodage en cours...' : 'Encoder dans l\'ADN'}
        </button>
      </form>

      {error && <div className="banner banner-error">{error}</div>}

      {result && (
        <div className="import-result">
          <header className="import-result-header">
            <h3>Séquence ADN générée : {result.filename}</h3>
            <a
              className="btn-primary"
              href={dnaFileDownloadUrl(result.id)}
              download
            >
              Télécharger le fichier ADN
            </a>
          </header>

          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-value">{formatBytes(result.byte_size)}</span>
              <span className="stat-label">Fichier original</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{formatSizeBases(result.bit_count)}</span>
              <span className="stat-label">Bits encodés</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{formatSizeBases(result.base_count)}</span>
              <span className="stat-label">Bases stockées</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{result.encoder}</span>
              <span className="stat-label">Encodeur</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{result.protection ?? '—'}</span>
              <span className="stat-label">Protection</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{result.seed ?? '—'}</span>
              <span className="stat-label">Graine utilisée</span>
            </div>
          </div>

          <p className="seed-note">
            Empreinte SHA-256 du fichier original : <code>{result.sha256}</code>
          </p>

          <h4>Aperçu de la séquence</h4>
          <DnaBlock value={result.preview} />
          {result.preview_truncated && (
            <p className="dna-truncated">
              Aperçu limité aux {result.preview.length} premières bases sur{' '}
              {formatSizeBases(result.base_count)}.
            </p>
          )}
        </div>
      )}

      <div className="stored-files">
        <h3>Fichiers ADN stockés en base</h3>
        {stored.length === 0 ? (
          <p className="stored-empty">Aucun fichier pour l'instant : importez-en un ci-dessus.</p>
        ) : (
          <ul className="stored-list">
            {stored.map((item) => (
              <li key={item.id}>
                <span className="stored-name">{item.filename}</span>
                <span className="stored-meta">
                  {formatSizeBases(item.base_count)} bases · encodeur {item.encoder}
                </span>
                <a className="btn-secondary" href={dnaFileDownloadUrl(item.id)} download>
                  Télécharger
                </a>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
