export function NegotiatorGridLogo({ size = 32 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      aria-label="NegotiatorGrid logo"
    >
      {/* 3x3 grid of squares with negotiation convergence */}
      <rect x="2" y="2" width="8" height="8" rx="1.5" stroke="#22d3ee" strokeWidth="1.5" opacity="0.4" />
      <rect x="12" y="2" width="8" height="8" rx="1.5" stroke="#22d3ee" strokeWidth="1.5" opacity="0.6" />
      <rect x="22" y="2" width="8" height="8" rx="1.5" stroke="#22d3ee" strokeWidth="1.5" opacity="0.4" />

      <rect x="2" y="12" width="8" height="8" rx="1.5" stroke="#22d3ee" strokeWidth="1.5" opacity="0.6" />
      <rect x="12" y="12" width="8" height="8" rx="1.5" stroke="#22d3ee" strokeWidth="1.5" fill="#22d3ee" fillOpacity="0.15" />
      <rect x="22" y="12" width="8" height="8" rx="1.5" stroke="#22d3ee" strokeWidth="1.5" opacity="0.6" />

      <rect x="2" y="22" width="8" height="8" rx="1.5" stroke="#22d3ee" strokeWidth="1.5" opacity="0.4" />
      <rect x="12" y="22" width="8" height="8" rx="1.5" stroke="#22d3ee" strokeWidth="1.5" opacity="0.6" />
      <rect x="22" y="22" width="8" height="8" rx="1.5" stroke="#22d3ee" strokeWidth="1.5" opacity="0.4" />

      {/* Convergence lines — buyer (blue) from top-left, seller (purple) from bottom-right */}
      <path d="M6 6 L16 16" stroke="#3b82f6" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M26 26 L16 16" stroke="#a855f7" strokeWidth="1.5" strokeLinecap="round" />

      {/* Deal point in center */}
      <circle cx="16" cy="16" r="2.5" fill="#22c55e" opacity="0.9" />
    </svg>
  );
}
