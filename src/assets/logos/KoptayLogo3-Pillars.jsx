// LOGO OPTION 3: Classical Pillars - Three Columns Design
// Symbolizes strength, stability, and justice
// Color scheme: lawPrimary (#2D3748) and lawSecondary (#548c8d)

const KoptayLogoPillars = ({ className = "w-48 h-48" }) => {
  return (
    <svg 
      viewBox="0 0 200 200" 
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Background rectangle */}
      <rect
        x="20"
        y="30"
        width="160"
        height="140"
        fill="#2D3748"
        rx="8"
      />
      
      {/* Three Classical Pillars */}
      <g transform="translate(50, 60)">
        {/* Left Pillar */}
        <g>
          <rect x="-8" y="0" width="16" height="4" fill="#548c8d" />
          <rect x="-6" y="4" width="12" height="60" fill="#F8F9FA" />
          <rect x="-8" y="64" width="16" height="6" fill="#548c8d" />
        </g>
        
        {/* Middle Pillar */}
        <g transform="translate(50, 0)">
          <rect x="-8" y="0" width="16" height="4" fill="#548c8d" />
          <rect x="-6" y="4" width="12" height="60" fill="#F8F9FA" />
          <rect x="-8" y="64" width="16" height="6" fill="#548c8d" />
        </g>
        
        {/* Right Pillar */}
        <g transform="translate(100, 0)">
          <rect x="-8" y="0" width="16" height="4" fill="#548c8d" />
          <rect x="-6" y="4" width="12" height="60" fill="#F8F9FA" />
          <rect x="-8" y="64" width="16" height="6" fill="#548c8d" />
        </g>
        
        {/* Foundation/Base */}
        <rect x="-12" y="70" width="124" height="4" fill="#548c8d" />
      </g>
      
      {/* Letter K integrated in middle */}
      <text
        x="100"
        y="115"
        textAnchor="middle"
        fill="#2D3748"
        fontSize="32"
        fontFamily="Georgia, serif"
        fontWeight="bold"
        opacity="0.3"
      >
        K
      </text>
      
      {/* Company name */}
      <text
        x="100"
        y="150"
        textAnchor="middle"
        fill="#F8F9FA"
        fontSize="22"
        fontFamily="Georgia, serif"
        fontWeight="bold"
        letterSpacing="2"
      >
        KOPTAY
      </text>
      <text
        x="100"
        y="165"
        textAnchor="middle"
        fill="#548c8d"
        fontSize="10"
        fontFamily="Georgia, serif"
        letterSpacing="3"
      >
        HUKUK BÜROSU
      </text>
    </svg>
  );
};

export default KoptayLogoPillars;
