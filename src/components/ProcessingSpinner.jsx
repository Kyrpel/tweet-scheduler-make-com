import './ProcessingSpinner.css';

function ProcessingSpinner({ text = "Processing article..." }) {
  return (
    <div className="processing-spinner">
      <div className="spinner"></div>
      <span className="processing-text">{text}</span>
    </div>
  );
}

export default ProcessingSpinner; 