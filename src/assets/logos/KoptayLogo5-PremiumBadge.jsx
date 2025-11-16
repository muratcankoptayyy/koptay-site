// LOGO OPTION 5: Premium Badge - Minimalist Professional
// Ultra-professional badge design with refined typography
// Color scheme: lawPrimary (#2D3748) and lawSecondary (#548c8d)

const KoptayLogoPremiumBadge = ({ className = "w-48 h-48" }) => {
  return (
    <svg 
      viewBox="0 0 200 200" 
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Outer circle with elegant stroke */}
      <circle
        cx="100"
        cy="100"
        r="85"
        fill="none"
        stroke="#548c8d"
        strokeWidth="1.5"
      />
      
      {/* Inner circle */}
      <circle
        cx="100"
        cy="100"
        r="75"
        fill="#2D3748"
      />
      
      {/* Decorative corner elements */}
      <g opacity="0.2">
        <path d="M 100 30 L 105 35 L 100 40 L 95 35 Z" fill="#548c8d" />
        <path d="M 170 100 L 165 105 L 160 100 L 165 95 Z" fill="#548c8d" />
        <path d="M 100 170 L 105 165 L 100 160 L 95 165 Z" fill="#548c8d" />
        <path d="M 30 100 L 35 105 L 40 100 L 35 95 Z" fill="#548c8d" />
      </g>
      
      {/* Legal book icon */}
      <g transform="translate(100, 75)">
        {/* Book */}
        <rect x="-18" y="-12" width="36" height="24" rx="2" fill="#548c8d" />
        <rect x="-16" y="-10" width="32" height="20" rx="1" fill="#F8F9FA" />
        
        {/* Book spine lines */}
        <line x1="-8" y1="-10" x2="-8" y2="10" stroke="#548c8d" strokeWidth="0.5" />
        <line x1="0" y1="-10" x2="0" y2="10" stroke="#548c8d" strokeWidth="0.5" />
        <line x1="8" y1="-10" x2="8" y2="10" stroke="#548c8d" strokeWidth="0.5" />
        
        {/* Paragraph symbol */}
        <text
          x="0"
          y="6"
          textAnchor="middle"
          fill="#2D3748"
          fontSize="16"
          fontFamily="Georgia, serif"
          fontWeight="bold"
        >
          §
        </text>
      </g>
      
      {/* Company name - top arc */}
      <path id="topArc" d="M 40 100 A 60 60 0 0 1 160 100" fill="none" />
      <text fontSize="11" fontFamily="Georgia, serif" letterSpacing="2" fill="#F8F9FA">
        <textPath href="#topArc" startOffset="50%" textAnchor="middle">
          KOPTAY
        </textPath>
      </text>
      
      {/* Subtitle - bottom arc */}
      <path id="bottomArc" d="M 160 100 A 60 60 0 0 1 40 100" fill="none" />
      <text fontSize="7" fontFamily="Georgia, serif" letterSpacing="3" fill="#548c8d">
        <textPath href="#bottomArc" startOffset="50%" textAnchor="middle">
          HUKUK BÜROSU
        </textPath>
      </text>
      
      {/* Center divider */}
      <line x1="60" y1="100" x2="85" y2="100" stroke="#548c8d" strokeWidth="1" opacity="0.5" />
      <line x1="115" y1="100" x2="140" y2="100" stroke="#548c8d" strokeWidth="1" opacity="0.5" />
      
      {/* Est. year (optional - can be customized) */}
      <text
        x="100"
        y="140"
        textAnchor="middle"
        fill="#548c8d"
        fontSize="8"
        fontFamily="Georgia, serif"
        letterSpacing="2"
      >
        EST. 2024
      </text>
    </svg>
  );
};

export default KoptayLogoPremiumBadge;
