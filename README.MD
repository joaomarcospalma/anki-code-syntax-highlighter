# Como adicionar o highlight.js ao add-on

1. Visite o site do [highlight.js](https://highlightjs.org/download/)

2. Selecione as linguagens que você deseja suportar (ou escolha "All" para todas)

3. Baixe o pacote compactado

4. Extraia o conteúdo e coloque os seguintes arquivos na pasta `web` do seu add-on:
   - `highlight.pack.js` (renomeie `highlight.min.js` para este nome)
   - A pasta `styles` inteira

Se preferir, você pode usar um CDN, mas isso exigirá conexão com a internet:

```javascript
// Em vez de usar arquivos locais, adicione isto ao seu código JavaScript
const script = document.createElement('script');
script.src = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js';
document.head.appendChild(script);

const css = document.createElement('link');
css.rel = 'stylesheet';
css.href = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/default.min.css';
document.head.appendChild(css);
```

No entanto, para melhor experiência offline, é recomendável usar os arquivos locais.