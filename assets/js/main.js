// Menu functionality
document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    const content = document.querySelector('.content');

    // Menu toggle
    menuToggle.addEventListener('click', () => {
        navMenu.classList.toggle('collapsed');
        content.classList.toggle('full-width');
    });

    // Submenu toggles
    document.querySelectorAll('.submenu-toggle').forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            const submenu = e.target.nextElementSibling;
            submenu.style.display = submenu.style.display === 'none' ? 'block' : 'none';
        });
    });

    // Smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});

// ASCII Art Animation
class ASCIIAnimation {
    constructor() {
        this.frames = [
            this.createFrame('simple'),
            this.createFrame('detailed'),
            this.createFrame('bordered')
        ];
        this.currentFrame = 0;
        this.animate();
    }

    createFrame(style) {
        // Create different ASCII art frames
        return style === 'simple' ?
            'PHILIP GREGORY\nBACHAS-DAUNERT' :
            style === 'detailed' ?
            '╔════════════════╗\n║ PHILIP GREGORY ║\n║ BACHAS-DAUNERT ║\n╚════════════════╝' :
            '┌────────────────┐\n│ PHILIP GREGORY │\n│ BACHAS-DAUNERT │\n└────────────────┘';
    }

    animate() {
        const header = document.querySelector('.ascii-header');
        if (header) {
            header.textContent = this.frames[this.currentFrame];
            this.currentFrame = (this.currentFrame + 1) % this.frames.length;
        }
        setTimeout(() => this.animate(), 2000);
    }
}

// Initialize ASCII animation
new ASCIIAnimation();

// Add 90s cursor trail effect
class CursorTrail {
    constructor() {
        this.trail = '★';
        this.points = [];
        this.init();
    }

    init() {
        document.addEventListener('mousemove', (e) => {
            this.points.push({
                x: e.pageX,
                y: e.pageY,
                life: 10
            });
            this.update();
        });
    }

    update() {
        this.points = this.points.filter(point => {
            point.life--;
            if (point.life <= 0) {
                return false;
            }
            return true;
        });
    }
}

// Initialize cursor trail
new CursorTrail();