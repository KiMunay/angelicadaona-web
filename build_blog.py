#!/usr/bin/env python3
"""Genera el blog a partir de content/blog/*.md  (solo librería estándar; lo corre Netlify en cada publicación).
Salida: blog/index.html, blog/<articulo>/index.html, blog/img/*, sitemap.xml, robots.txt"""
import os, re, glob, html, json, shutil, math
from shrink import shrink
from datetime import date
DOMINIO = os.environ.get('SITE_URL', 'https://angelicadaona.com.ar').rstrip('/')
SRC, OUT = 'content/blog', 'blog'
MESES = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
PAGINAS = ['', 'diagnostico.html', 'encontrar.html', 'contenido.html', 'elegir.html', 'reservar.html', 'contacto.html']
esc = lambda t: html.escape(t, quote=True)
def fecha_es(d): y, m, dd = map(int, d.split('-')); return f'{dd} de {MESES[m-1]} de {y}'

# ---------- markdown mínimo ----------
def inline(t):
    t = esc(t)
    t = re.sub(r'!\[([^\]]*)\]\(([^)\s]+)\)', lambda m: f'<img src="{img_src(m.group(2))}" alt="{m.group(1)}" loading="lazy">', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', r'<a href="\2">\1</a>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', t)
    return t
def img_src(n): return n if re.match(r'(https?:|/|\.\./)', n) else 'blog/img/' + n
def md(texto):
    out, lista, para = [], None, []
    def cierra_p():
        if para: out.append('<p>' + inline(' '.join(para)) + '</p>'); para.clear()
    def cierra_l():
        nonlocal lista
        if lista: out.append(f'</{lista}>'); lista = None
    for ln in texto.split('\n'):
        s = ln.strip()
        if not s: cierra_p(); cierra_l(); continue
        m = re.match(r'(#{2,3})\s+(.*)', s)
        if m: cierra_p(); cierra_l(); n = len(m.group(1)); out.append(f'<h{n}>{inline(m.group(2))}</h{n}>'); continue
        m = re.match(r'([-*])\s+(.*)', s) or None
        m2 = re.match(r'\d+\.\s+(.*)', s)
        if m or m2:
            cierra_p(); tag = 'ul' if m else 'ol'
            if lista != tag: cierra_l(); out.append(f'<{tag}>'); lista = tag
            out.append('<li>' + inline((m or m2).group(m and 2 or 1)) + '</li>'); continue
        if s.startswith('>'): cierra_p(); cierra_l(); out.append('<blockquote><p>' + inline(s.lstrip('> ')) + '</p></blockquote>'); continue
        if s == '---': cierra_p(); cierra_l(); out.append('<hr>'); continue
        if re.fullmatch(r'!\[[^\]]*\]\([^)\s]+\)', s): cierra_p(); cierra_l(); out.append('<figure>' + inline(s) + '</figure>'); continue
        cierra_l(); para.append(s)
    cierra_p(); cierra_l(); return '\n'.join(out)

def lee(path):
    t = open(path, encoding='utf-8').read().lstrip('﻿')
    m = re.match(r'---\s*\n(.*?)\n---\s*\n(.*)', t, re.S)
    if not m: raise SystemExit(f'Falta el encabezado (---) en {path}')
    meta = {}
    for ln in m.group(1).split('\n'):
        if ':' in ln: k, v = ln.split(':', 1); meta[k.strip().lower()] = v.strip()
    for k in ('titulo', 'fecha', 'resumen'):
        if not meta.get(k): raise SystemExit(f'Falta "{k}:" en {path}')
    meta['slug'] = os.path.splitext(os.path.basename(path))[0]; meta['cuerpo'] = m.group(2)
    return meta

# ---------- plantilla: se arma desde contacto.html (menú, estilos y pie del sitio) ----------
base = open('contacto.html', encoding='utf-8').read()
head, resto = base.split('</head>', 1)
head = re.sub(r'<title>.*?</title>\n?|<meta name="description"[^>]*>\n?|<meta property="og:[^>]*>\n?|<meta name="twitter:[^>]*>\n?|<link rel="canonical"[^>]*>\n?|<script type="application/ld\+json">.*?</script>\n?', '', head, flags=re.S)
cuerpo_ini = resto[:resto.index('<section class="sp-hero"')]
mf = re.search(r'</div>\s*<div class="wrap">\s*<footer>', resto)
if not mf: raise SystemExit('No encuentro el pie en contacto.html')
cuerpo_fin = resto[mf.start():]
CSS = '''<style>
.bl-wrap{max-width:1120px;margin:0 auto}.bl-hero{padding-block:56px 12px}.bl-hero h1{margin:6px 0 14px;font-size:clamp(30px,4.4vw,48px);line-height:1.15;max-width:22ch;text-wrap:balance}.bl-hero p{max-width:60ch}
.bl-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px;padding-block:28px 64px}
.bl-card{background:var(--surface,#0F3E50);border:1px solid var(--line,#2A5B6D);border-radius:16px;overflow:hidden;display:flex;flex-direction:column;min-width:0;transition:transform .2s,border-color .2s}
.bl-card:hover{transform:translateY(-3px);border-color:#E58B63}.bl-card a{color:inherit;text-decoration:none;display:flex;flex-direction:column;height:100%}
.bl-card img{display:block;width:100%;height:auto;aspect-ratio:1200/630;object-fit:cover}
.bl-card a>div{padding:22px 24px 26px;display:flex;flex-direction:column;gap:10px}.bl-card h2{margin:0;font:700 22px/1.3 var(--display,Ubuntu,sans-serif)}
.bl-card p{margin:0;color:var(--muted,#A8BEC6);font-size:16px;line-height:1.55}
.bl-meta{display:flex;flex-wrap:wrap;gap:6px 14px;font:500 13px/1.4 var(--display,Ubuntu,sans-serif);letter-spacing:.06em;text-transform:uppercase;color:#E58B63}
.bl-meta span+span:before{content:"·";margin-right:14px;color:#2A5B6D}
.bl-art{max-width:760px;margin:0 auto;padding-block:48px 24px}.bl-art h1{margin:10px 0 16px;text-wrap:balance;font-size:clamp(28px,4vw,42px);line-height:1.15}
.bl-by{display:flex;align-items:center;gap:12px;margin:18px 0 26px;font-size:15px;color:var(--muted,#A8BEC6)}.bl-by img{width:48px;height:48px;border-radius:50%;object-fit:cover;border:2px solid #E58B63}
.bl-cover{display:block;width:100%;height:auto;aspect-ratio:1200/630;object-fit:cover;border-radius:14px;border:2px solid #E58B63;margin-bottom:34px}
.bl-body{font-size:19px;line-height:1.75}.bl-body h2{margin:44px 0 12px;font:700 28px/1.25 var(--display,Ubuntu,sans-serif);text-wrap:balance}.bl-body h3{margin:30px 0 8px;font:700 21px/1.3 var(--display,Ubuntu,sans-serif)}
.bl-body p{margin:0 0 18px}.bl-body ul,.bl-body ol{margin:0 0 20px;padding-left:1.3em;display:flex;flex-direction:column;gap:8px}.bl-body a{color:#E58B63}
.bl-body blockquote{margin:24px 0;padding:6px 0 6px 20px;border-left:3px solid #E58B63}.bl-body figure{margin:26px 0}.bl-body img{max-width:100%;height:auto;border-radius:12px}
.bl-body hr{border:0;border-top:1px solid #2A5B6D;margin:34px 0}.bl-back{display:inline-block;margin:6px 0 0;color:#E58B63;text-decoration:none;font-weight:700}
.bl-cta{margin:44px 0 0;padding:30px 28px;background:var(--surface,#0F3E50);border:1px solid var(--line,#2A5B6D);border-radius:16px;display:flex;flex-direction:column;gap:14px;align-items:flex-start}.bl-cta h2{margin:0;font:700 24px/1.3 var(--display,Ubuntu,sans-serif)}.bl-cta p{margin:0;color:var(--muted,#A8BEC6)}
.bl-more{padding-block:20px 56px}.bl-more h2{font:700 24px/1.3 var(--display,Ubuntu,sans-serif);margin:0 0 16px}
@media (max-width:760px){.bl-grid{grid-template-columns:minmax(0,1fr)}.bl-body{font-size:17px}.bl-body h2{font-size:24px}.bl-cta{padding:24px 20px}}
</style>'''

CSS = shrink(CSS)
def rebase(t, p):
    return re.sub(r'(href|src)="(?!https?:|#|mailto:|tel:|data:|//)([^"]+)"', lambda m: f'{m.group(1)}="{p}{m.group(2)}"', t)
def pagina(titulo, desc, canon, og, cuerpo, p, extra=''):
    h = head + f'<title>{esc(titulo)}</title>\n<meta name="description" content="{esc(desc)}">\n<link rel="canonical" href="{canon}">\n<meta property="og:type" content="{"article" if "BlogPosting" in extra else "website"}">\n<meta property="og:locale" content="es_AR">\n<meta property="og:site_name" content="Angélica Daona">\n<meta property="og:title" content="{esc(titulo)}">\n<meta property="og:description" content="{esc(desc)}">\n<meta property="og:url" content="{canon}">\n<meta property="og:image" content="{og}">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:title" content="{esc(titulo)}">\n<meta name="twitter:description" content="{esc(desc)}">\n<meta name="twitter:image" content="{og}">\n{extra}{CSS}\n</head>'
    fab = '<a class="fab" href="https://wa.me/5493812164856?text=Hola%20Ang%C3%A9lica%2C%20quiero%20contarte%20sobre%20mi%20alojamiento">Escribime por WhatsApp</a>\n'
    ini = cuerpo_ini.replace('<body>', '<body>\n' + fab, 1) if 'class="fab"' not in cuerpo_ini else cuerpo_ini
    return rebase(h + ini + cuerpo + cuerpo_fin, p)

def titulo_pag(a):
    t = a.get('titulo_seo') or a['titulo']
    return t if len(t) + 16 > 60 else t + ' | Angélica Daona'

arts = sorted((lee(f) for f in glob.glob(SRC + '/*.md')), key=lambda a: a['fecha'], reverse=True)
arts = [a for a in arts if a['fecha'] <= date.today().isoformat() or os.environ.get('VER_FUTUROS')]   # fecha futura = programado
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
if os.path.isdir(SRC + '/img'): shutil.copytree(SRC + '/img', OUT + '/img')
def og_de(a): return f'{DOMINIO}/blog/img/{a["imagen"]}' if a.get('imagen') else f'{DOMINIO}/share-index.jpg'
def tarjeta(a, p=''):
    img = f'<img src="blog/img/{esc(a["imagen"])}" alt="{esc(a.get("alt",""))}" width="1200" height="630" loading="lazy">' if a.get('imagen') else ''
    return f'<article class="bl-card"><a href="blog/{a["slug"]}/index.html">{img}<div><div class="bl-meta"><span>{esc(a.get("categoria","Blog"))}</span><span>{fecha_es(a["fecha"])}</span></div><h2>{esc(a["titulo"])}</h2><p>{esc(a["resumen"])}</p></div></a></article>'

# ---------- artículos ----------
for i, a in enumerate(arts):
    palabras = len(re.findall(r'\w+', a['cuerpo'])); mins = max(1, math.ceil(palabras / 200))
    cuerpo_html = md(a['cuerpo'])
    portada = f'<img class="bl-cover" src="blog/img/{esc(a["imagen"])}" alt="{esc(a.get("alt",""))}" width="1200" height="630" fetchpriority="high">' if a.get('imagen') else ''
    otros = [x for x in arts if x is not a][:2]
    mas = ('<section class="bl-more"><h2>Seguí leyendo</h2><div class="bl-grid" style="padding:0">' + ''.join(tarjeta(x) for x in otros) + '</div></section>') if otros else ''
    cuerpo = f'''<article class="bl-art"><a class="bl-back" href="blog/index.html">← Blog</a>
<div class="bl-meta" style="margin-top:22px"><span>{esc(a.get("categoria","Blog"))}</span><span>{fecha_es(a["fecha"])}</span><span>{mins} min de lectura</span></div>
<h1>{esc(a["titulo"])}</h1>
<div class="bl-by"><img src="angelica.webp" alt="Angélica Daona" width="48" height="48"><span>Por Angélica Daona</span></div>
{portada}
<div class="bl-body">
{cuerpo_html}
</div>
<aside class="bl-cta"><h2>¿Querés saber por dónde empezar con tu alojamiento?</h2><p>Contame cómo te encuentran hoy y te digo por dónde conviene empezar.</p><a class="btn btn-main" href="contacto.html">Escribime</a></aside>
</article>
{mas}'''
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "BlogPosting", "headline": a['titulo'], "description": a['resumen'], "datePublished": a['fecha'], "dateModified": a.get('actualizado', a['fecha']), "inLanguage": "es-AR",
         "image": og_de(a), "mainEntityOfPage": f"{DOMINIO}/blog/{a['slug']}/", "author": {"@type": "Person", "name": "Angélica Daona", "url": DOMINIO + "/"},
         "publisher": {"@type": "Organization", "name": "Angélica Daona", "logo": {"@type": "ImageObject", "url": DOMINIO + "/logo.webp"}}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Inicio", "item": DOMINIO + "/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": DOMINIO + "/blog/"},
            {"@type": "ListItem", "position": 3, "name": a['titulo'], "item": f"{DOMINIO}/blog/{a['slug']}/"}]}]}
    extra = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>\n'
    os.makedirs(f"{OUT}/{a['slug']}")
    open(f"{OUT}/{a['slug']}/index.html", 'w', encoding='utf-8').write(
        pagina(titulo_pag(a), a.get('descripcion', a['resumen']), f"{DOMINIO}/blog/{a['slug']}/", og_de(a), cuerpo, '../../', extra))

# ---------- índice ----------
lista = ''.join(tarjeta(a) for a in arts) or '<p>Pronto vas a encontrar acá los primeros artículos.</p>'
idx = f'''<div class="bl-wrap"><section class="bl-hero"><div class="eyebrow">Blog</div><h1>Ideas para que tu alojamiento sea encontrado, elegido y reservado</h1><p>Respuestas claras a las preguntas que se hacen los dueños de alojamientos, una por semana.</p></section>
<section class="bl-grid" aria-label="Artículos">{lista}</section></div>'''
ld = {"@context": "https://schema.org", "@type": "Blog", "name": "Blog de Angélica Daona", "url": DOMINIO + "/blog/", "inLanguage": "es-AR",
      "blogPost": [{"@type": "BlogPosting", "headline": a['titulo'], "url": f"{DOMINIO}/blog/{a['slug']}/", "datePublished": a['fecha']} for a in arts]}
open(OUT + '/index.html', 'w', encoding='utf-8').write(pagina('Blog para dueños de alojamientos | Angélica Daona', 'Artículos sobre marketing digital para alojamientos de Argentina: cómo ser encontrado, elegido y reservado.', DOMINIO + '/blog/', DOMINIO + '/share-index.jpg', idx, '../', '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>\n'))

# ---------- página 404 ----------
c404 = '<section class="bl-wrap bl-hero" style="padding-block:72px"><div class="eyebrow">Error 404</div><h1>Esta página no existe</h1><p>Puede que el enlace haya cambiado. Podés volver al inicio, mirar los servicios o leer el blog.</p><p style="margin-top:22px;display:flex;gap:12px;flex-wrap:wrap"><a class="btn btn-main" href="index.html">Ir al inicio</a><a class="btn btn-ghost" href="blog/index.html">Ver el blog</a></p></section>'
h4 = pagina('Página no encontrada | Angélica Daona', 'Esta página no existe.', DOMINIO + '/', DOMINIO + '/share-index.jpg', c404, '/')
h4 = h4.replace('<meta name="robots" content="index,follow,max-image-preview:large">', '<meta name="robots" content="noindex">').replace('<link rel="canonical" href="' + DOMINIO + '/">\n', '')
open('404.html', 'w', encoding='utf-8').write(h4)

# ---------- sitemap y robots ----------
urls = [f'{DOMINIO}/{p}' for p in PAGINAS] + [DOMINIO + '/blog/'] + [f"{DOMINIO}/blog/{a['slug']}/" for a in arts]
lm = {f"{DOMINIO}/blog/{a['slug']}/": a.get('actualizado', a['fecha']) for a in arts}
open('sitemap.xml', 'w', encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{u}</loc>' + (f'<lastmod>{lm[u]}</lastmod>' if u in lm else '') + '</url>\n' for u in urls) + '</urlset>\n')
open('robots.txt', 'w').write(f'User-agent: *\nAllow: /\nDisallow: /content/\nDisallow: /build_blog.py\nDisallow: /shrink.py\nDisallow: /LEEME.md\n\nSitemap: {DOMINIO}/sitemap.xml\n')
print(f'Blog listo: {len(arts)} artículo(s)')
