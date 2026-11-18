export default function SummaryPanel({ result }) {
  const { stats, integrity, original_message, received_message, seed } = result;
  const propagated = stats.errors_injected - stats.errors_corrected;

  const statItems = [
    { label: 'Bits transmis', value: stats.bits },
    { label: 'Bases émises', value: stats.bases_source },
    { label: 'Bases transmises (avec redondance)', value: stats.bases_sent },
    { label: 'Erreurs injectées', value: stats.errors_injected },
    { label: 'Erreurs corrigées', value: stats.errors_corrected },
    { label: 'Erreurs non corrigées', value: propagated },
  ];

  return (
    <section className="card summary-panel">
      <header className="summary-header">
        <h2>Bilan de la transmission</h2>
        <span className={`badge ${integrity ? 'badge-ok' : 'badge-error'} badge-large`}>
          {integrity
            ? 'Intégrité préservée : le message reçu est identique au message original'
            : 'Intégrité altérée : le message reçu diffère du message original'}
        </span>
      </header>

      <div className="compare-grid">
        <div className="compare-box">
          <h3>Message original</h3>
          <p className="text-block">{original_message}</p>
        </div>
        <div className="compare-box">
          <h3>Message reçu</h3>
          <p className={`text-block ${integrity ? '' : 'text-corrupted'}`}>{received_message}</p>
        </div>
      </div>

      <div className="stats-grid">
        {statItems.map((item) => (
          <div className="stat-item" key={item.label}>
            <span className="stat-value">{item.value}</span>
            <span className="stat-label">{item.label}</span>
          </div>
        ))}
      </div>

      <p className="seed-note">
        Graine aléatoire utilisée : <code>{seed}</code> — réutiliser cette valeur permet de reproduire
        exactement les mêmes erreurs de canal.
      </p>
    </section>
  );
}
