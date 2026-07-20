(() => {
  const body = document.body;
  const menuToggle = document.querySelector('.menu-toggle');
  const mobileNav = document.getElementById('mobileNav');
  const progress = document.getElementById('scrollProgress');

  if (menuToggle && mobileNav) {
    menuToggle.addEventListener('click', () => {
      const open = body.classList.toggle('menu-open');
      menuToggle.setAttribute('aria-expanded', String(open));
    });
    mobileNav.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
      body.classList.remove('menu-open');
      menuToggle.setAttribute('aria-expanded', 'false');
    }));
  }

  document.querySelectorAll('[data-language-link]').forEach((link) => {
    link.addEventListener('click', (event) => {
      if (window.location.hash) {
        event.preventDefault();
        window.location.href = `${link.href}${window.location.hash}`;
      }
    });
  });

  const updateProgress = () => {
    if (!progress) return;
    const max = document.documentElement.scrollHeight - window.innerHeight;
    progress.style.width = `${max > 0 ? (window.scrollY / max) * 100 : 0}%`;
  };
  window.addEventListener('scroll', updateProgress, { passive: true });
  updateProgress();

  const revealItems = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08 });
    revealItems.forEach((item) => observer.observe(item));
  } else {
    revealItems.forEach((item) => item.classList.add('visible'));
  }

  const tocLinks = [...document.querySelectorAll('.project-toc a[href^="#"]')];
  if (tocLinks.length && 'IntersectionObserver' in window) {
    const headings = tocLinks.map((link) => document.querySelector(link.getAttribute('href'))).filter(Boolean);
    const headingObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          tocLinks.forEach((link) => link.classList.toggle('active', link.getAttribute('href') === `#${entry.target.id}`));
        }
      });
    }, { rootMargin: '-18% 0px -70% 0px', threshold: 0 });
    headings.forEach((heading) => headingObserver.observe(heading));
  }

  const copyButton = document.querySelector('.copy-email');
  if (copyButton) {
    copyButton.addEventListener('click', async () => {
      const email = copyButton.dataset.email || '';
      try {
        await navigator.clipboard.writeText(email);
        const original = copyButton.textContent;
        copyButton.textContent = copyButton.dataset.copiedLabel || 'Copied';
        setTimeout(() => { copyButton.textContent = original; }, 1800);
      } catch {
        window.location.href = `mailto:${email}`;
      }
    });
  }

  const lightbox = document.getElementById('lightbox');
  if (lightbox) {
    const image = lightbox.querySelector('img');
    const caption = lightbox.querySelector('p');
    const close = lightbox.querySelector('.lightbox-close');
    let previousFocus = null;

    const openLightbox = (src, alt, trigger) => {
      previousFocus = trigger;
      image.src = src;
      image.alt = alt || '';
      caption.textContent = alt || '';
      lightbox.classList.add('open');
      lightbox.setAttribute('aria-hidden', 'false');
      body.style.overflow = 'hidden';
      close.focus();
    };
    const closeLightbox = () => {
      lightbox.classList.remove('open');
      lightbox.setAttribute('aria-hidden', 'true');
      image.src = '';
      body.style.overflow = '';
      if (previousFocus) previousFocus.focus();
    };
    document.querySelectorAll('[data-lightbox-src]').forEach((button) => {
      button.addEventListener('click', () => openLightbox(button.dataset.lightboxSrc, button.dataset.lightboxAlt, button));
    });
    close.addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', (event) => { if (event.target === lightbox) closeLightbox(); });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && lightbox.classList.contains('open')) closeLightbox();
    });
  }
})();
