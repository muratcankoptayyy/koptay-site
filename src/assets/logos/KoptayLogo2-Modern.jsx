// LOGO OPTION 2: Modern Minimalist - Geometric K with Legal Elements
// Clean, contemporary design emphasizing the "K" initial
// Color scheme: lawPrimary (#2D3748) and lawSecondary (#548c8d)

const KoptayLogoModern = ({ className = "w-48 h-48" }) => {
  return (
    <svg 
      viewBox="0 0 200 200" 
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Outer circle */}
      <circle
        cx="100"
        cy="100"
        r="75"
        fill="none"
        stroke="#548c8d"
        strokeWidth="2"
      />
      
      {/* Inner background circle */}
      <circle
        cx="100"
        cy="100"
        r="65"
        fill="#2D3748"
      />
      
      {/* Stylized "K" made with geometric shapes */}
      <g transform="translate(100, 100)">
        {/* Vertical bar of K */}
        <rect x="-25" y="-35" width="8" height="70" fill="#548c8d" />
        
        {/* Upper diagonal of K */}
        <path
          d="M -17 -5 L 15 -35 L 23 -30 L -9 0 Z"
          fill="#F8F9FA"
        />
        
        {/* Lower diagonal of K */}
        <path
          d="M -9 0 L 23 30 L 15 35 L -17 5 Z"
          fill="#548c8d"
        />
        
        {/* Small pillar/column accent (legal symbol) */}
        <g transform="translate(28, 0)">
          <rect x="-2" y="-25" width="4" height="50" fill="#F8F9FA" opacity="0.6" />
        </g>
      </g>
      
      {/* Text below */}
      <text
        x="100"
        y="190"
        textAnchor="middle"
        fill="#2D3748"
        fontSize="18"
        fontFamily="Georgia, serif"
        fontWeight="bold"
        letterSpacing="3"
      >
        KOPTAY
      </text>
    </svg>
  );
};

export default KoptayLogoModern;
