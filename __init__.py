"""
Code Syntax Highlighter Add-on para Anki
===================================
Este add-on permite adicionar blocos de código com syntax highlighting nos cartões do Anki.
"""

import os
import json
from aqt import mw, gui_hooks
from aqt.qt import QAction, QMenu, qconnect
from aqt.utils import showInfo
from aqt.editor import Editor
from anki.hooks import wrap

# Carregar configurações
config = mw.addonManager.getConfig(__name__) or {}

# Caminhos para os recursos
addon_path = os.path.dirname(__file__)
web_path = os.path.join(addon_path, "web")

# Lista de linguagens suportadas
supported_languages = config.get('supportedLanguages', ['python', 'javascript'])
default_language = config.get('defaultLanguage', 'python')

# Injetar os assets JS/CSS no editor
# No método on_editor_init, modifique o script para carregar os arquivos de linguagem
def on_editor_init(editor):
    """Adiciona os scripts e estilos necessários ao editor"""
    editor.web.eval("""
        // Carregar highlight.js se não estiver carregado
        if (typeof hljs === 'undefined') {
            const script = document.createElement('script');
            script.src = '/_addons/code_syntax_highlighter/web/highlight.pack.js';
            document.head.appendChild(script);
            
            // Carregar o CSS do tema
            const style = document.createElement('link');
            style.rel = 'stylesheet';
            style.href = '/_addons/code_syntax_highlighter/web/styles/default.min.css';
            document.head.appendChild(style);
            
            // Registrar o caminho para os arquivos de linguagem
            script.onload = function() {
                hljs.configure({
                    languages: {},
                    langPath: '/_addons/code_syntax_highlighter/web/languages/'
                });
            };
        }
    """)

# Adicionar o botão ao editor
def add_button(buttons, editor):
    """Adiciona o botão de código no editor"""
    button = editor.addButton(
        icon=os.path.join(addon_path, "web/icon_code.png"),
        cmd="insertCodeBlock",
        func=insert_code_block,
        tip="Inserir bloco de código (Ctrl+Shift+C)",
        keys="Ctrl+Shift+C"
    )
    buttons.append(button)
    return buttons

def insert_code_block(editor):
    """Insere um bloco de código no editor"""
    # Preparar a lista de linguagens para o menu JavaScript
    lang_list_js = json.dumps(supported_languages)
    default_lang = default_language
    
    # Código JavaScript para executar no editor
    js_code = f"""
    (function() {{
        const languages = {lang_list_js};
        const defaultLang = "{default_lang}";
        
        // Função para criar o menu de seleção de linguagem
        function createLanguageMenu() {{
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
            
            languages.forEach(lang => {{
                const item = document.createElement('div');
                item.textContent = lang;
                item.style.padding = '5px 10px';
                item.style.cursor = 'pointer';
                item.style.borderRadius = '2px';
                
                item.onmouseover = () => {{
                    item.style.background = '#f0f0f0';
                }};
                
                item.onmouseout = () => {{
                    item.style.background = 'transparent';
                }};
                
                item.onclick = () => {{
                    insertCodeBlockWithLanguage(lang);
                    document.body.removeChild(menu);
                }};
                
                menu.appendChild(item);
            }});
            
            return menu;
        }}
        
        // Função para inserir o bloco de código com a linguagem selecionada
        function insertCodeBlockWithLanguage(language) {{
            const selectedText = window.getSelection().toString();
            const codeBlock = `\`\`\`${{language}}
${{selectedText || 'Digite seu código aqui'}}
\`\`\``;
            
            document.execCommand('insertText', false, codeBlock);
            
            // Aplicar o highlight após inserir
            setTimeout(() => {{
                document.querySelectorAll('pre code').forEach((block) => {{
                    hljs.highlightBlock(block);
                }});
            }}, 100);
        }}
        
        // Posicionar e mostrar o menu
        const selection = window.getSelection();
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        
        const menu = createLanguageMenu();
        document.body.appendChild(menu);
        
        const editorRect = document.querySelector('.editor').getBoundingClientRect();
        menu.style.left = (rect.left + window.scrollX) + 'px';
        menu.style.top = (rect.bottom + window.scrollY) + 'px';
        
        // Remover o menu se clicar fora dele
        document.addEventListener('click', function closeMenu(e) {{
            if (!menu.contains(e.target)) {{
                if (document.body.contains(menu)) {{
                    document.body.removeChild(menu);
                }}
                document.removeEventListener('click', closeMenu);
            }}
        }});
    }})();
    """
    
    editor.web.eval(js_code)

# Processador de cartões para aplicar syntax highlighting
def on_card_render(text, card, phase):
    """
    Processa o HTML do cartão para aplicar syntax highlighting aos blocos de código
    """
    import re
    
    # Padrão para encontrar blocos de código markdown
    code_pattern = r'```(\w+)?\n([\s\S]*?)```'
    
    def replace_code_block(match):
        language = match.group(1) or default_language
        code = match.group(2)
        
        # Sanitizar o código para segurança
        code = code.replace('<', '&lt;').replace('>', '&gt;')
        
        # Criar o HTML com a classe da linguagem para o highlight.js
        return f'<pre><code class="language-{language}">{code}</code></pre>'
    
    # Substituir os blocos de código
    processed_text = re.sub(code_pattern, replace_code_block, text)
    
    # Adicionar script para aplicar o highlight (apenas se houver blocos de código)
    if '```' in text:
        processed_text += """
        <script>
        // Verificar se highlight.js já está carregado
        if (typeof hljs === 'undefined') {
            // Carregar highlight.js dinamicamente
            const script = document.createElement('script');
            script.src = '/_addons/code_syntax_highlighter/web/highlight.pack.js';
            script.onload = function() {
                // Após carregar, aplicar o highlighting
                document.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightBlock(block);
                });
            };
            document.head.appendChild(script);
            
            // Carregar o CSS do tema
            const style = document.createElement('link');
            style.rel = 'stylesheet';
            style.href = '/_addons/code_syntax_highlighter/web/styles/default.min.css';
            document.head.appendChild(style);
        } else {
            // Se já carregado, aplicar o highlighting
            document.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightBlock(block);
            });
        }
        </script>
        """
    
    return processed_text

# Configurar hooks
gui_hooks.editor_did_init.append(on_editor_init)
gui_hooks.editor_did_init_buttons.append(add_button)
gui_hooks.card_will_show.append(on_card_render)

# Adicionar menu de configuração
def show_config():
    """Mostrar janela de configuração do add-on"""
    showInfo("Configuração do Code Syntax Highlighter.\n\nPara alterar configurações, edite o arquivo config.json na pasta do add-on.")

# Adicionar menu ao Anki
action = QAction("Code Syntax Highlighter", mw)
qconnect(action.triggered, show_config)
mw.form.menuTools.addAction(action)