import { useEffect, useState } from 'react';
import { fetchCatalog } from './lib/api';
import ImportPanel from './components/ImportPanel';
import DemoPage from './components/DemoPage';

export default function App() {
  const [page, setPage] = useState('home');
  const [catalog, setCatalog] = useState(null);

  useEffect(() => {
    let cancelled = false;
    fetchCatalog()
      .then((data) => {
        if (!cancelled) setCatalog(data);
      })
      .catch(() => {
        if (!cancelled) setCatalog({});
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // Navigation partageable et bouton retour du navigateur (#accueil / #demo)
  useEffect(() => {
    const syncFromHash = () => {
      setPage(window.location.hash === '#demo' ? 'demo' : 'home');
    };
    syncFromHash();
    window.addEventListener('hashchange', syncFromHash);
    return () => window.removeEventListener('hashchange', syncFromHash);
  }, []);

  const goTo = (next) => {
    window.location.hash = next === 'demo' ? '#demo' : '#accueil';
  };

  return (
    <div className="app">
      <header className="site-header">
        <h1>Stockage de données sur ADN</h1>
        <p>Dépôt de fichiers encodés en ADN — et démonstration de la chaîne de transmission complète</p>

        <nav className="site-nav">
          <button
            type="button"
            className={`nav-btn ${page === 'home' ? 'nav-btn-active' : ''}`}
            onClick={() => goTo('home')}
          >
            Accueil · Dépôt ADN
          </button>
          <button
            type="button"
            className={`nav-btn ${page === 'demo' ? 'nav-btn-active' : ''}`}
            onClick={() => goTo('demo')}
          >
            Chaîne de transmission
          </button>
        </nav>
      </header>

      <main className="content">
        {page === 'home' ? (
          <>
            <section className="card home-hero">
              <h2>Bienvenue sur le dépôt ADN</h2>
              <p>
                Déposez un fichier ci-dessous : son contenu est converti en code ADN par l'API,
                stocké en base de données, puis la séquence vous est proposée en téléchargement.
              </p>
              <ol className="home-steps">
                <li>Importer un fichier (texte ou binaire).</li>
                <li>Le contenu est encodé en bases azotées (A, T, C, G) et enregistré en base.</li>
                <li>Télécharger le fichier ADN, immédiatement ou plus tard depuis la liste.</li>
              </ol>
            </section>

            <ImportPanel />
          </>
        ) : (
          <DemoPage catalog={catalog} />
        )}
      </main>

      <footer className="site-footer">
        <p>Projet S9 — Stockage de données sur ADN · Démonstration pédagogique de la chaîne de transmission</p>
      </footer>
    </div>
  );
}
