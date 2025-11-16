// LOGO OPTION 1: Classic Law Firm - Scales of Justice with Shield
// Professional, traditional design with modern touches
// Color scheme: lawPrimary (#2D3748) and lawSecondary (#548c8d)

const KoptayLogoClassic = ({ className = "w-48 h-48" }) => {
  return (
    <svg 
      viewBox="0 0 200 200" 
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Shield Background */}
      <path
        d="M100 20 L160 40 L160 100 Q160 150 100 180 Q40 150 40 100 L40 40 Z"
        fill="#2D3748"
        stroke="#548c8d"
        strokeWidth="2"
      />
      
      {/* Scales of Justice */}
      <g transform="translate(100, 80)">
        {/* Central pole */}
        <rect x="-2" y="0" width="4" height="60" fill="#548c8d" />
        
        {/* Balance beam */}
        <rect x="-40" y="15" width="80" height="3" fill="#548c8d" />
        
        {/* Left scale */}
        <g>
          <line x1="-30" y1="16" x2="-30" y2="30" stroke="#548c8d" strokeWidth="1.5" />
          <path
            d="M -40 30 L -20 30 L -20 35 L -40 35 Z"
            fill="none"
            stroke="#548c8d"
            strokeWidth="1.5"
          />
        </g>
        
        {/* Right scale */}
        <g>
          <line x1="30" y1="16" x2="30" y2="30" stroke="#548c8d" strokeWidth="1.5" />
          <path
            d="M 20 30 L 40 30 L 40 35 L 20 35 Z"
            fill="none"
            stroke="#548c8d"
            strokeWidth="1.5"
          />
        </g>
        
        {/* Base */}
        <rect x="-15" y="60" width="30" height="4" fill="#548c8d" />
      </g>
      
      {/* Text */}
      <text
        x="100"
        y="165"
        textAnchor="middle"
        fill="#F8F9FA"
        fontSize="20"
        fontFamily="Georgia, serif"
        fontWeight="bold"
      >
        KOPTAY
      </text>
      <text
        x="100"
        y="180"
        textAnchor="middle"
        fill="#548c8d"
        fontSize="10"
        fontFamily="Georgia, serif"
        letterSpacing="2"
      >
        HUKUK BÜROSU
      </text>
    </svg>
  );
};

export default KoptayLogoClassic;
