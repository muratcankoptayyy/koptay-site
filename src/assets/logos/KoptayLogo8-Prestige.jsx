// LOGO OPTION 8: Prestige Crest - Luxury Law Firm
// High-end crest design with heraldic elements
// Color scheme: lawPrimary (#2D3748) and lawSecondary (#548c8d)

const KoptayLogoPrestige = ({ className = "w-48 h-48" }) => {
  return (
    <svg 
      viewBox="0 0 200 220" 
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Shield crest background */}
      <path
        d="M 100 20 
           L 160 45 
           Q 162 48 162 52
           L 162 110 
           Q 162 140 145 160
           Q 125 180 100 195
           Q 75 180 55 160
           Q 38 140 38 110
           L 38 52
           Q 38 48 40 45
           Z"
        fill="#2D3748"
        stroke="#548c8d"
        strokeWidth="2.5"
      />
      
      {/* Inner shield decoration */}
      <path
        d="M 100 35 
           L 150 55 
           L 150 105 
           Q 150 130 100 175
           Q 50 130 50 105
           L 50 55
           Z"
        fill="none"
        stroke="#548c8d"
        strokeWidth="1"
        opacity="0.3"
      />
      
      {/* Top banner ribbon */}
      <path
        d="M 50 55 L 150 55 L 145 65 L 55 65 Z"
        fill="#548c8d"
      />
      
      {/* Central emblem - Stylized K with laurel */}
      <g transform="translate(100, 110)">
        {/* Letter K */}
        <g>
          <rect x="-20" y="-25" width="8" height="50" fill="#F8F9FA" />
          <path d="M -12 -5 L 12 -25 L 16 -21 L -8 -1 Z" fill="#548c8d" />
          <path d="M -8 1 L 16 21 L 12 25 L -12 5 Z" fill="#548c8d" />
        </g>
        
        {/* Left laurel branch */}
        <g opacity="0.7">
          <path
            d="M -25 -10 Q -30 -5 -30 0 Q -30 5 -25 10"
            fill="none"
            stroke="#548c8d"
            strokeWidth="1.5"
          />
          <circle cx="-28" cy="-8" r="2" fill="#548c8d" />
          <circle cx="-31" cy="-3" r="2" fill="#548c8d" />
          <circle cx="-31" cy="3" r="2" fill="#548c8d" />
          <circle cx="-28" cy="8" r="2" fill="#548c8d" />
        </g>
        
        {/* Right laurel branch */}
        <g opacity="0.7">
          <path
            d="M 25 -10 Q 30 -5 30 0 Q 30 5 25 10"
            fill="none"
            stroke="#548c8d"
            strokeWidth="1.5"
          />
          <circle cx="28" cy="-8" r="2" fill="#548c8d" />
          <circle cx="31" cy="-3" r="2" fill="#548c8d" />
          <circle cx="31" cy="3" r="2" fill="#548c8d" />
          <circle cx="28" cy="8" r="2" fill="#548c8d" />
        </g>
      </g>
      
      {/* Bottom decorative element */}
      <g transform="translate(100, 165)">
        <path
          d="M -20 0 L 0 -5 L 20 0 L 0 5 Z"
          fill="#548c8d"
        />
      </g>
      
      {/* Main text */}
      <text
        x="100"
        y="62"
        textAnchor="middle"
        fill="#F8F9FA"
        fontSize="12"
        fontFamily="Georgia, serif"
        fontWeight="bold"
        letterSpacing="3"
      >
        KOPTAY
      </text>
      
      {/* Bottom text on ribbon */}
      <g transform="translate(100, 200)">
        <path
          d="M -50 -5 L -55 5 L -20 5 L -20 -5 Z"
          fill="#548c8d"
        />
        <path
          d="M 50 -5 L 55 5 L 20 5 L 20 -5 Z"
          fill="#548c8d"
        />
        <rect x="-20" y="-5" width="40" height="10" fill="#548c8d" />
        
        <text
          x="0"
          y="3"
          textAnchor="middle"
          fill="#F8F9FA"
          fontSize="8"
          fontFamily="Georgia, serif"
          letterSpacing="2"
        >
          HUKUK BÜROSU
        </text>
      </g>
    </svg>
  );
};

export default KoptayLogoPrestige;
