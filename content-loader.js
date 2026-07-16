(function () {
  'use strict';

  const FRONT_MATTER_RE = /^---\s*\n([\s\S]*?)\n---\s*\n?([\s\S]*)$/;
  const IMAGE_RE = /^!\[(.*?)\]\((.*?)\)\s*$/;
  const YOUTUBE_RE = /^@\[youtube\]\((\S+?)(?:\s+["“](.*?)["”])?\)\s*$/;
  const LINK_RE = /\[([^\]]+)\]\(([^)]+)\)/g;
  const LINKS_ONLY_RE = /^(?:\s*\[[^\]]+\]\([^)]+\)\s*)+$/;
  const CONTENT_FILES = { zh: 'content.md', en: 'content_en.md' };

  function normalizeLanguage(language) {
    return language === 'en' ? 'en' : 'zh';
  }

  function parseFrontMatter(markdown) {
    const normalized = String(markdown).replace(/\r\n/g, '\n');
    const match = normalized.match(FRONT_MATTER_RE);
    if (!match) throw new Error('Missing Markdown front matter.');

    const meta = {};
    match[1].split('\n').forEach(rawLine => {
      const line = rawLine.trim();
      if (!line || line.startsWith('#')) return;
      const separator = line.indexOf(':');
      if (separator < 0) throw new Error(`Invalid metadata line: ${rawLine}`);
      const key = line.slice(0, separator).trim();
      const value = line.slice(separator + 1).trim().replace(/^['"]|['"]$/g, '');
      meta[key] = value;
    });
    return { meta, body: match[2].trim() };
  }

  function resolvePath(projectId, value) {
    const path = String(value).trim();
    if (/^(?:https?:|mailto:|data:|#)/i.test(path)) return path;
    return new URL(path, new URL(`${projectId}/`, document.baseURI)).href;
  }

  function getYoutubeId(value) {
    const source = String(value).trim();
    const patterns = [
      /youtu\.be\/([A-Za-z0-9_-]{6,})/,
      /youtube(?:-nocookie)?\.com\/(?:watch\?v=|embed\/|shorts\/)([A-Za-z0-9_-]{6,})/,
    ];
    for (const pattern of patterns) {
      const match = source.match(pattern);
      if (match) return match[1];
    }
    return source;
  }

  function parseBlocks(body, projectId, language) {
    const blocks = [];
    let paragraphLines = [];

    function flushParagraph() {
      if (!paragraphLines.length) return;
      const paragraph = paragraphLines.join('\n').trim();
      paragraphLines = [];
      if (!paragraph) return;

      if (LINKS_ONLY_RE.test(paragraph)) {
        const links = [];
        LINK_RE.lastIndex = 0;
        let match;
        while ((match = LINK_RE.exec(paragraph)) !== null) {
          links.push({ label: match[1].trim(), href: resolvePath(projectId, match[2].trim()) });
        }
        blocks.push({ kind: 'buttons', links });
        return;
      }

      blocks.push({ kind: 'paragraph', text: paragraph });
    }

    String(body).split('\n').forEach(rawLine => {
      const line = rawLine.replace(/\s+$/, '');
      const stripped = line.trim();

      if (!stripped) {
        flushParagraph();
        return;
      }

      if (stripped.startsWith('## ')) {
        flushParagraph();
        blocks.push({ kind: 'heading', text: stripped.slice(3).trim() });
        return;
      }

      const imageMatch = stripped.match(IMAGE_RE);
      if (imageMatch) {
        flushParagraph();
        blocks.push({ kind: 'image', caption: imageMatch[1].trim(), src: resolvePath(projectId, imageMatch[2].trim()) });
        return;
      }

      const youtubeMatch = stripped.match(YOUTUBE_RE);
      if (youtubeMatch) {
        flushParagraph();
        blocks.push({
          kind: 'youtube',
          id: getYoutubeId(youtubeMatch[1]),
          caption: (youtubeMatch[2] || (language === 'en' ? 'YouTube Video' : 'YouTube 视频')).trim(),
        });
        return;
      }

      paragraphLines.push(line);
    });

    flushParagraph();
    return blocks;
  }

  function parseProject(markdown, projectId, language) {
    const { meta, body } = parseFrontMatter(markdown);
    const database = {
      title: meta.title || projectId,
      tabTitle: meta.tab_title || meta.title || projectId,
      tag: meta.tag || '',
      type: meta.type || '',
      role: meta.role || '',
      time: meta.time || '',
      caption: meta.caption || '',
    };
    const content = { blocks: parseBlocks(body, projectId, language) };

    if (meta.hero) {
      content.hero = {
        src: resolvePath(projectId, meta.hero),
        caption: meta.hero_caption || meta.title || '',
      };
      if (/^(?:(?:100|[1-9]?\d)%|\d{2,4}px)$/.test(meta.hero_width || '')) {
        content.hero.width = meta.hero_width;
      }
    }

    return { database, content };
  }

  window.loadSiteContent = async function loadSiteContent(projectIds, requestedLanguage) {
    const language = normalizeLanguage(requestedLanguage);
    window.SITE_CONTENT_BY_LANGUAGE = window.SITE_CONTENT_BY_LANGUAGE || {};
    window.SITE_CONTENT_BY_LANGUAGE[language] = window.SITE_CONTENT_BY_LANGUAGE[language] || { database: {}, content: {} };

    if (location.protocol !== 'http:' && location.protocol !== 'https:') {
      return window.SITE_CONTENT_BY_LANGUAGE[language];
    }

    const target = window.SITE_CONTENT_BY_LANGUAGE[language];
    const filename = CONTENT_FILES[language];

    await Promise.all(projectIds.map(async projectId => {
      try {
        const response = await fetch(`${projectId}/${filename}`, { cache: 'no-store' });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const parsed = parseProject(await response.text(), projectId, language);
        target.database[projectId] = parsed.database;
        target.content[projectId] = parsed.content;
      } catch (error) {
        console.warn(`Unable to load ${projectId}/${filename}; generated fallback content is being used.`, error);
      }
    }));

    return target;
  };
})();
