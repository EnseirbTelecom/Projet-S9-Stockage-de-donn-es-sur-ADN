export default function Pipeline({ steps, current, onSelect }) {
  return (
    <div className="pipeline">
      {steps.map((step, i) => {
        const isDone = i < current;
        const isActive = i === current;

        return (
          <div className="pipeline-node-wrap" key={step.id}>
            {i > 0 && <div className={`pipeline-link ${isDone || isActive ? 'link-done' : ''}`} />}
            <button
              type="button"
              className={`pipeline-node ${isDone ? 'done' : ''} ${isActive ? 'active' : ''}`}
              onClick={() => onSelect(i)}
            >
              <span className="node-index">{isDone ? 'OK' : i + 1}</span>
              <span className="node-label">{step.label}</span>
            </button>
          </div>
        );
      })}
    </div>
  );
}
