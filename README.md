# Monitoramento de Cotações

---

## Execução do código 

Para executar o agente de monitoramento, siga os comandos a seguir:

### **1. Preparar o Ambiente**

- **1º:** `instalar as bibliotecas necessárias`
 ```json
  {
    "pip install selenium lxml python-dotenv"
  }
```
- **2º:** `Certificar-se de que o Microsoft Edge está instalado no sistema`

### **2. Executar a Aplicação**

- **1º:** `Comando para iniciar o monitoramento`
```json
  {
    "python main.py"
  }
```
  ### **3. Interação via console**

- **1º:** `Nome de Usuário: Apenas letras, mínimo de 3 caracteres`
- **2º:** `URL Alvo: O link do site que contém a informação (ex: site de notícias ou bolsa).`
- **3º:** `XPath: O caminho exato do elemento que deve ser "escaneado".`

## Logs de Auditoria e Atividade

### **1. Rastreabilidade**

O sistema gera um arquivo chamado log_usuario.txt que funciona como uma caixa-preta de todas as ações.

- **1º:** `O que é registrado no log`

- Identificação: Quem iniciou a sessão (Nome do Usuário).
- Entradas de Teclado: Registra cada URL e cada XPath que o usuário digitou no console.
- Validações: Registra se o usuário tentou inserir nomes inválidos ou URLs malformadas.

- **2º:** `Estrutura do Log`

Cada linha segue o padrão:
DATA HORA - NÍVEL - [Usuário: NOME] - MENSAGEM

## Fluxo de Automação (Salvamento)

## Processamento de Mudanças
 
Se o agente detectar que o valor do XPath mudou em relação à primeira captura, ele inicia o processo de salvamento automático e eniva uma mensagem via Selenium

- **1º:** `Execução do Salvamento`

- Nova Aba: O robô abre uma aba secundária sem fechar a original.
- Formulário: Acessa https://www.selenium.dev/selenium/web/web-form.html.
- Preenchimento: Escreve automaticamente no campo textarea o relatório:
Quem detectou a mudança.
Qual era o valor antigo.
Qual é o novo valor.
- Submissão: Clica no botão Submit para finalizar a operação.