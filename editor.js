/**
 * editor.js - Script para adicionar funcionalidade de syntax highlighting ao editor do Anki
 */

// Função para processar e destacar blocos de código
function processCodeBlocks() {
    // Selecionar todos os blocos de código
    document.querySelectorAll('pre code').forEach((block) => {
        // Verificar se o bloco já foi processado
        if (!block.classList.contains('hljs')) {
            hljs.highlightBlock(block);
        }
    });
}

// Função para converter a marcação de código em elementos HTML
function convertCodeMarkup() {
    const editorContent = document.querySelector('.editor-field');
    if (!editorContent) return;
    
    // Encontrar todos os blocos de código marcados com triplo backtick
    const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
    let match;
    let contentHTML = editorContent.innerHTML;
    
    while ((match = codeBlockRegex.exec(contentHTML)) !== null) {
        const fullMatch = match[0];
        const language = match[1] || 'plaintext';
        const code = match[2].replace(/</g, '&lt;').replace(/>/g, '&gt;');
        
        // Substituir a marcação pelo HTML adequado
        const replacement = `<pre><code class="language-${language}">${code}</code></pre>`;
        contentHTML = contentHTML.replace(fullMatch, replacement);
    }
    
    editorContent.innerHTML = contentHTML;
    
    // Aplicar o highlighting
    processCodeBlocks();
}

// Função para inserir um bloco de código
function insertCodeBlock(language) {
    const selection = window.getSelection();
    const selectedText = selection.toString();
    
    // Criar o bloco de código
    const codeBlock = `\`\`\`${language}
${selectedText || 'Digite seu código aqui'}
\`\`\``;
    
    // Inserir no editor
    document.execCommand('insertText', false, codeBlock);
    
    // Converter a marcação em HTML com highlighting
    setTimeout(convertCodeMarkup, 50);
}

// Função para mostrar o menu de seleção de linguagem
function showLanguageMenu(languages, callback) {
    // Criar o elemento do menu
    const menu = document.createElement('div');
    menu.className = 'code-lang-menu';
    menu.style.position = 'absolute';
    menu.style.zIndex = '1000';
    menu.style.background = '#fff';
    menu.style.border = '1px solid #ccc';
    menu.style.borderRadius = '4px';
    menu.style.padding = '5px';
    menu.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
    menu.style.maxHeight = '300px';
    menu.style.overflowY = 'auto';
    
    // Adicionar as opções de linguagem
    languages.forEach(lang => {
        const item = document.createElement('div');
        item.textContent = lang;
        item.style.padding = '5px 10px';
        item.style.cursor = 'pointer';
        
        item.onmouseover = () => { item.style.background = '#f0f0f0'; };
        item.onmouseout = () => { item.style.background = 'transparent'; };
        
        item.onclick = () => {
            callback(lang);
            document.body.removeChild(menu);
        };
        
        menu.appendChild(item);
    });
    
    // Posicionar e adicionar o menu ao documento
    const selection = window.getSelection();
    const range = selection.getRangeAt(0);
    const rect = range.getBoundingClientRect();
    
    document.body.appendChild(menu);
    
    menu.style.left = (rect.left + window.scrollX) + 'px';
    menu.style.top = (rect.bottom + window.scrollY) + 'px';
    
    // Remover o menu se clicar fora dele
    document.addEventListener('click', function closeMenu(e) {
        if (!menu.contains(e.target)) {
            if (document.body.contains(menu)) {
                document.body.removeChild(menu);
            }
            document.removeEventListener('click', closeMenu);
        }
    });
}

// Adicionar a função ao escopo global para que possa ser chamada pelo Python
window.showCodeLanguageMenu = function(languages, defaultLanguage) {
    showLanguageMenu(languages, (language) => {
        insertCodeBlock(language);
    });
};

// Inicializar quando o documento estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Observar mudanças no editor para processar blocos de código
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' || mutation.type === 'characterData') {
                processCodeBlocks();
            }
        });
    });
    
    // Configurar e iniciar o observer
    const editorContent = document.querySelector('.editor-field');
    if (editorContent) {
        observer.observe(editorContent, { 
            childList: true, 
            characterData: true,
            subtree: true 
        });
    }
    
    // Processar blocos existentes
    processCodeBlocks();
});