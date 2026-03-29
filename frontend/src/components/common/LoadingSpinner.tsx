export default function LoadingSpinner({ text = 'Loading...' }: { text?: string }) {
  return (
    <div className="loading-overlay">
      <div className="spinner" />
      <span>{text}</span>
    </div>
  );
}
