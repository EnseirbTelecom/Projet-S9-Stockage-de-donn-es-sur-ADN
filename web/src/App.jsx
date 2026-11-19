import { useEffect, useState } from 'react';
import { runTransmission, fetchCatalog } from './lib/api';
import ControlPanel from './components/ControlPanel';
import Pipeline from './components/Pipeline';
import StepDetail from './components/StepDetail';
import SummaryPanel from './components/SummaryPanel';

const STEP_DURATION = 1500;

const ARCHITECTURE = [
  {
    role: 'Classe abstraite (core/)',
    items: [
      ['BaseEncodeur', 'core/base_encoder.py — contrat encode(data) -> str'],
      ['BaseDecodeur', 'core/base_decoder.py — contrat decode(sequence) -> str'],
      ['BaseCanal', 'core/base_channel.py — contrat transmit(sequence) -> dict'],
      ['BaseProtection', 'core/base_protection.py — contrats protect / restore'],
    ],
  },
  {
    role: 'Implémentations',
    items: [
      ['One2OneEncoder', 'encoders/ — 0 -> A/T, 1 -> C/G'],
      ['One2OneDecoder', 'decoders/ — A/T -> 0, C/G -> 1'],
      ['SubstitutionChannel', 'channels/ — substitutions aléatoires de bases'],
      ['ReplicationProtection', 'protections/ — réplication ×3 et vote majoritaire'],
    ],
  },
  {
    role: 'Wrappers (wrappers/)',
    items: [
      ['EncodeWrapper / DecodeWrapper', 'interface homogène pour encoder et décoder'],
      ['ChannelWrapper', 'interface homogène pour les modèles de canal'],
      ['ProtectionWrapper', 'interface homogène pour la protection'],
    ],
  },
];

export default function App() {
  const [result, setResult] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [catalog, setCatalog] = useState(null);

  // Catalogue des implémentations (sélecteurs de stratégies)
  useEffect(() => {
    let cancelled = false;
    fetchCatalog()
      .then((data) => {
        if (!cancelled) setCatalog(data);
      })
      .catch(() => {
        // Le panneau fonctionne sans catalogue (les sélecteurs sont masqués)
        if (!cancelled) setCatalog({});
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const start = async (params) => {
    setLoading(true);
    setPlaying(false);
    setError(null);
    try {
      const data = await runTransmission(params);
      setResult(data);
      setCurrentStep(0);
      setPlaying(true);
    } catch (e) {
      setError(e.message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const isComplete = result && currentStep >= result.steps.length - 1;

  useEffect(() => {
    if (!playing || !result) return undefined;

    if (currentStep >= result.steps.length - 1) {
      setPlaying(false);
      return undefined;
    }

    const timer = setTimeout(() => setCurrentStep((s) => s + 1), STEP_DURATION);
    return () => clearTimeout(timer);
  }, [playing, currentStep, result]);

  const goTo = (index) => {
    setPlaying(false);
    setCurrentStep(Math.max(0, Math.min(index, result ? result.steps.length - 1 : 0)));
  };

  const togglePlay = () => {
    if (!result) return;
    if (isComplete) {
      setCurrentStep(0);
      setPlaying(true);
    } else {
      setPlaying((p) => !p);
    }
  };

  return (
    <div className="app">
      <header className="site-header">
        <h1>Stockage de données sur ADN</h1>
        <p>Démonstration de la chaîne de transmission complète — encodage, protection, canal bruité et décodage</p>
      </header>

      <main className="content">
        <ControlPanel catalog={catalog} onRun={start} loading={loading} />

        {error && <div className="banner banner-error">{error}</div>}

        {result && (
          <>
            <section className="card pipeline-card">
              <Pipeline steps={result.steps} current={currentStep} onSelect={goTo} />

              <div className="player-controls">
                <button type="button" className="btn-secondary" onClick={() => goTo(0)} disabled={loading}>
                  Revenir au début
                </button>
                <button type="button" className="btn-secondary" onClick={() => goTo(currentStep - 1)} disabled={currentStep === 0}>
                  Étape précédente
                </button>
                <button type="button" className="btn-primary btn-play" onClick={togglePlay}>
                  {isComplete ? 'Rejouer la transmission' : playing ? 'Pause' : 'Lecture'}
                </button>
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => goTo(currentStep + 1)}
                  disabled={isComplete}
                >
                  Étape suivante
                </button>
                <span className="progress-note">
                  Étape {currentStep + 1} / {result.steps.length}
                </span>
              </div>
            </section>

            <StepDetail step={result.steps[currentStep]} />

            {isComplete && <SummaryPanel result={result} />}
          </>
        )}

        {!result && !error && (
          <section className="card intro-card">
            <h2>Comment fonctionne la démonstration</h2>
            <ol className="intro-list">
              <li>Saisir un message puis lancer la transmission : celui-ci est converti en bits (UTF-8).</li>
              <li>L'encodeur <code>one2one</code> transforme chaque bit en base azotée : 0 devient A ou T, 1 devient C ou G.</li>
              <li>Si la protection est activée, chaque base est répliquée trois fois avant transmission.</li>
              <li>Le canal introduit un taux d'erreurs configurable (substitutions de bases, comme lors du séquençage).</li>
              <li>À la réception, le vote majoritaire corrige les bases altérées, puis la séquence est décodée et le message reconstruit.</li>
              <li>Chaque étape est visualisées en détail : cliquez sur un nœud du pipeline ou laissez l'animation se dérouler.</li>
            </ol>
          </section>
        )}

        <section className="card architecture-card">
          <h2>Architecture logicielle</h2>
          <p className="architecture-intro">
            Chaque composant de la chaîne suit la même architecture : une classe abstraite définissant le
            contrat, un wrapper offrant une interface homogène, et une ou plusieurs implémentations
            concrètes testables indépendamment via les endpoints de l'API.
          </p>
          <div className="architecture-grid">
            {ARCHITECTURE.map((group) => (
              <div className="arch-group" key={group.role}>
                <h3>{group.role}</h3>
                <ul>
                  {group.items.map(([name, desc]) => (
                    <li key={name}>
                      <strong>{name}</strong>
                      <span>{desc}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <p>Projet S9 — Stockage de données sur ADN · Démonstration pédagogique de la chaîne de transmission</p>
      </footer>
    </div>
  );
}
