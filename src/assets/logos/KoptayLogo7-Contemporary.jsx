// LOGO OPTION 7: Contemporary Law - Modern Professional
// Contemporary design with clean geometric elements
// Color scheme: lawPrimary (#2D3748) and lawSecondary (#548c8d)

const KoptayLogoContemporary = ({ className = "w-48 h-48" }) => {
  return (
    <svg 
      viewBox="0 0 200 200" 
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Outer square frame with rounded corners */}
      <rect
        x="20"
        y="20"
        width="160"
        height="160"
        rx="8"
        fill="none"
        stroke="#548c8d"
        strokeWidth="2"
      />
      
      {/* Inner background */}
      <rect
        x="30"
        y="30"
        width="140"
        height="140"
        rx="4"
        fill="#2D3748"
      />
      
      {/* Stylized letter K with law elements */}
      <g transform="translate(100, 100)">
        {/* Left vertical bar of K */}
        <rect x="-45" y="-50" width="12" height="100" fill="#F8F9FA" />
        
        {/* Upper diagonal - integrated with paragraph symbol */}
        <path
          d="M -33 -15 L 25 -50 L 35 -43 L -23 -8 Z"
          fill="#548c8d"
        />
        
        {/* Lower diagonal */}
        <path
          d="M -23 8 L 35 43 L 25 50 L -33 15 Z"
          fill="#548c8d"
        />
        
        {/* Legal symbol integration - small paragraph symbol */}
        <text
          x="30"
          y="5"
          fill="#F8F9FA"
          fontSize="20"
          fontFamily="Georgia, serif"
          fontWeight="bold"
        >
          §
        </text>
      </g>
      
      {/* Text below the icon */}
      <text
        x="100"
        y="185"
        textAnchor="middle"
        fill="#2D3748"
        fontSize="22"
        fontFamily="Georgia, serif"
        fontWeight="bold"
        letterSpacing="4"
      >
        KOPTAY
      </text>
      
      {/* Decorative corner accents */}
      <g fill="#548c8d" opacity="0.6">
        <circle cx="30" cy="30" r="3" />
        <circle cx="170" cy="30" r="3" />
        <circle cx="30" cy="170" r="3" />
        <circle cx="170" cy="170" r="3" />
      </g>
      
      {/* Subtle legal reference lines */}
      <g opacity="0.2">
        <line x1="40" y1="40" x2="60" y2="40" stroke="#548c8d" strokeWidth="1" />
        <line x1="140" y1="40" x2="160" y2="40" stroke="#548c8d" strokeWidth="1" />
        <line x1="40" y1="160" x2="60" y2="160" stroke="#548c8d" strokeWidth="1" />
        <line x1="140" y1="160" x2="160" y2="160" stroke="#548c8d" strokeWidth="1" />
      </g>
    </svg>
  );
};

export default KoptayLogoContemporary;
