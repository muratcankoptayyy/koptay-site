// LOGO OPTION 6: Executive Serif - Sophisticated Typography Focus
// High-end, executive style logo with emphasis on typography
// Color scheme: lawPrimary (#2D3748) and lawSecondary (#548c8d)

const KoptayLogoExecutive = ({ className = "w-48 h-48" }) => {
  return (
    <svg 
      viewBox="0 0 300 120" 
      className={className}
      xmlns="http://www.w3.org/2000/svg"
      preserveAspectRatio="xMidYMid meet"
    >
      {/* Background subtle gradient rectangle */}
      <defs>
        <linearGradient id="execGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#2D3748" stopOpacity="0.05" />
          <stop offset="50%" stopColor="#548c8d" stopOpacity="0.1" />
          <stop offset="100%" stopColor="#2D3748" stopOpacity="0.05" />
        </linearGradient>
      </defs>
      
      <rect x="0" y="0" width="300" height="120" fill="url(#execGradient)" />
      
      {/* Left decorative element - legal scale icon simplified */}
      <g transform="translate(30, 60)">
        {/* Minimalist scales */}
        <line x1="0" y1="-20" x2="0" y2="15" stroke="#548c8d" strokeWidth="2" />
        <line x1="-15" y1="-20" x2="15" y2="-20" stroke="#548c8d" strokeWidth="2" />
        <circle cx="-15" cy="-20" r="3" fill="#548c8d" />
        <circle cx="15" cy="-20" r="3" fill="#548c8d" />
        <rect x="-8" y="15" width="16" height="3" fill="#2D3748" />
      </g>
      
      {/* Main text - KOPTAY */}
      <text
        x="150"
        y="60"
        textAnchor="middle"
        fill="#2D3748"
        fontSize="42"
        fontFamily="Georgia, serif"
        fontWeight="bold"
        letterSpacing="8"
      >
        KOPTAY
      </text>
      
      {/* Decorative line under main text */}
      <line x1="80" y1="72" x2="220" y2="72" stroke="#548c8d" strokeWidth="1.5" />
      
      {/* Subtitle */}
      <text
        x="150"
        y="90"
        textAnchor="middle"
        fill="#548c8d"
        fontSize="11"
        fontFamily="Georgia, serif"
        letterSpacing="6"
        fontWeight="normal"
      >
        HUKUK BÜROSU
      </text>
      
      {/* Right decorative element - legal pillar */}
      <g transform="translate(270, 60)">
        <rect x="-3" y="-25" width="6" height="35" fill="#548c8d" />
        <rect x="-6" y="-28" width="12" height="3" fill="#2D3748" />
        <rect x="-6" y="10" width="12" height="3" fill="#2D3748" />
      </g>
      
      {/* Corner flourishes */}
      <g opacity="0.3">
        <path d="M 10 10 L 25 10 L 25 12 L 12 12 L 12 25 L 10 25 Z" fill="#548c8d" />
        <path d="M 290 10 L 275 10 L 275 12 L 288 12 L 288 25 L 290 25 Z" fill="#548c8d" />
        <path d="M 10 110 L 25 110 L 25 108 L 12 108 L 12 95 L 10 95 Z" fill="#548c8d" />
        <path d="M 290 110 L 275 110 L 275 108 L 288 108 L 288 95 L 290 95 Z" fill="#548c8d" />
      </g>
    </svg>
  );
};

export default KoptayLogoExecutive;
