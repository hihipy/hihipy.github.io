// 90s-style cursor trail effect
class Trail {
    constructor() {
      this.trail = '★';
      this.positions = [];
      this.maxLength = 10;
      this.trailElements = [];
      
      this.init();
    }
  
    init() {
      document.addEventListener('mousemove', (e) => this.handleMouseMove(e));
      
      // Create trail elements
      for (let i = 0; i < this.maxLength; i++) {
        const element = document.createElement('div');
        element.className = 'trail-star';
        element.innerHTML = this.trail;
        document.body.appendChild(element);
        this.trailElements.push(element);
      }
    }
  
    handleMouseMove(e) {
      // Add new position
      this.positions.push({ x: e.pageX, y: e.pageY });
      
      // Remove old positions
      if (this.positions.length > this.maxLength) {
        this.positions.shift();
      }
      
      // Update trail elements
      this.trailElements.forEach((element, index) => {
        const position = this.positions[this.positions.length - 1 - index];
        if (position) {
          element.style.left = `${position.x}px`;
          element.style.top = `${position.y}px`;
          element.style.opacity = 1 - (index / this.maxLength);
        }
      });
    }
  }
  
  // Retro text effect for headers
  function initRetroText() {
    const headers = document.querySelectorAll('h1, h2');
    headers.forEach(header => {
      header.classList.add('retro-text');
      
      // Add hover effect
      header.addEventListener('mouseover', () => {
        header.style.animation = 'none';
        header.offsetHeight; // Trigger reflow
        header.style.animation = 'retroGlow 1s infinite';
      });
      
      header.addEventListener('mouseout', () => {
        header.style.animation = 'none';
      });
    });
  }
  
  // ASCII art animation
  function animateAsciiArt() {
    const asciiArts = document.querySelectorAll('.ascii-art');
    asciiArts.forEach(art => {
      art.style.opacity = '0';
      art.style.transform = 'translateY(20px)';
      
      setTimeout(() => {
        art.style.transition = 'all 1s ease';
        art.style.opacity = '1';
        art.style.transform = 'translateY(0)';
      }, 100);
    });
  }
  
  // "Under Construction" banner
  function addConstructionBanner() {
    const banner = document.createElement('div');
    banner.className = 'construction-banner';
    banner.innerHTML = `
      <span class="blink">🚧</span>
      ALWAYS IMPROVING
      <span class="blink">🚧</span>
    `;
    document.body.appendChild(banner);
  }
  
  // Initialize everything when document is ready
  document.addEventListener('DOMContentLoaded', () => {
    new Trail();
    initRetroText();
    animateAsciiArt();
    addConstructionBanner();
  });