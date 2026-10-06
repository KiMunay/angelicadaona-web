# Cómo publicar un artículo nuevo (una vez por semana)

Todo se hace desde la página de GitHub, sin instalar nada. Netlify actualiza el sitio solo.

## Para publicar
1. Entrá a tu repositorio en GitHub y abrí la carpeta `content` → `blog`.
2. **Subí la foto:** entrá a `content/blog/img`, tocá **Add file → Upload files**, arrastrá la foto (JPG, 1200 × 630 px, de menos de 300 KB) y tocá **Commit changes**.
3. **Creá el artículo:** volvé a `content/blog`, tocá **Add file → Create new file** y ponele de nombre el título corto del artículo, sin tildes ni espacios y terminado en `.md`. Ejemplo: `como-responder-resenas.md`.
4. Pegá esta plantilla y cambiá lo que corresponda:

```
---
titulo: Cómo responder reseñas, las buenas y las malas
fecha: 2026-10-13
resumen: Una o dos frases que cuentan de qué trata el artículo. Aparece en la lista del blog y en Google.
imagen: como-responder-resenas.jpg
alt: Descripción corta de la foto
categoria: Reseñas
---
Acá empieza el texto. La primera frase responde directamente la pregunta.

## Un título de sección

Un párrafo normal. Podés poner **negrita** y *cursiva*.

- Una lista
- Con puntos

[Texto de un enlace](diagnostico.html)
```

5. Tocá **Commit changes**. En un minuto el artículo está en `angelicadaona.com.ar/blog/`, en el sitemap y listo para compartir.

## Reglas
- Lo que está entre `---` arriba es obligatorio: `titulo`, `fecha` (año-mes-día) y `resumen`. `imagen`, `alt` y `categoria` son recomendables.
- Títulos de sección con `##` (y `###` para subsecciones). El título principal ya lo arma el blog.
- Para enlazar a otra página del sitio escribí solo su nombre: `contacto.html`, `reservar.html`.
- Para poner una foto dentro del texto, subila a `content/blog/img` y escribí `![Descripción](nombre-de-la-foto.jpg)`.
- Si ponés una fecha futura, el artículo no se muestra hasta que el sitio se vuelva a publicar ese día o después.

## Para corregir o borrar
Abrí el archivo en `content/blog`, tocá el lápiz para editar (o los tres puntos → Delete file) y **Commit changes**.

## Configuración inicial (se hace una sola vez)
1. Creá una cuenta gratuita en github.com y un repositorio nuevo (por ejemplo `angelicadaona-web`).
2. En el repositorio, tocá **Add file → Upload files**, arrastrá todo el contenido de esta carpeta y **Commit changes**.
3. En Netlify: **Add new site → Import an existing project → GitHub**, elegí el repositorio. Netlify toma solo la configuración del archivo `netlify.toml`.
4. En **Domain management** de Netlify, agregá `angelicadaona.com.ar` y seguí los pasos que te indica.
