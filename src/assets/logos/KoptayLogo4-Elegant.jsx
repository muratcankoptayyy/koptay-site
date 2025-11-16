// LOGO OPTION 4: Elegant Monogram - Interlocked K and Scales
// Sophisticated, memorable design with intertwined elements
// Color scheme: lawPrimary (#2D3748) and lawSecondary (#548c8d)

const KoptayLogoElegant = ({ className = "w-48 h-48" }) => {
  return (
    <svg 
      viewBox="0 0 200 200" 
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Hexagonal background */}
      <path
        d="M 100 25 L 160 60 L 160 130 L 100 165 L 40 130 L 40 60 Z"
        fill="#2D3748"
        stroke="#548c8d"
        strokeWidth="3"
      />
      
      {/* Decorative inner hexagon */}
      <path
        d="M 100 40 L 145 65 L 145 120 L 100 145 L 55 120 L 55 65 Z"
        fill="none"
        stroke="#548c8d"
        strokeWidth="1"
        opacity="0.3"
      />
      
      {/* Stylized K with scale integration */}
      <g transform="translate(100, 95)">
        {/* K vertical */}
        <rect x="-30" y="-40" width="10" height="80" fill="#F8F9FA" />
        
        {/* K upper diagonal with scale pan */}
        <path d="M -20 -10 L 10 -40 L 15 -35 L -15 -5 Z" fill="#548c8d" />
        
        {/* Scale chain for upper */}
        <line x1="12" y1="-37" x2="12" y2="-28" stroke="#F8F9FA" strokeWidth="2" />
        <ellipse cx="12" cy="-25" rx="12" ry="4" fill="none" stroke="#F8F9FA" strokeWidth="2" />
        
        {/* K lower diagonal with scale pan */}
        <path d="M -15 5 L 15 35 L 10 40 L -20 10 Z" fill="#548c8d" />
        
        {/* Scale chain for lower */}
        <line x1="12" y1="37" x2="12" y2="28" stroke="#F8F9FA" strokeWidth="2" />
        <ellipse cx="12" cy="25" rx="12" ry="4" fill="none" stroke="#F8F9FA" strokeWidth="2" />
        
        {/* Balance point */}
        <circle cx="0" cy="0" r="6" fill="#548c8d" stroke="#F8F9FA" strokeWidth="2" />
      </g>
      
      {/* Text */}
      <text
        x="100"
        y="185"
        textAnchor="middle"
        fill="#2D3748"
        fontSize="20"
        fontFamily="Georgia, serif"
        fontWeight="bold"
        letterSpacing="4"
      >
        KOPTAY
      </text>
    </svg>
  );
};

export default KoptayLogoElegant;
