# Projetos II <br> Labinho

## Apresentação
O grupo desenvolveu um site para a máteria de Projetos II do curso Projeto Desenvolve Itabira para atender as demandas de um restaurante da cidade chamado Labinho. Diante disso, incorporamos no site um 
banco de dados para cadastro de clientes e produtos, uma interface dinâmica e atrativa e um carrinho para os usuários fazerem seus pedidos. 

## Projeto
Conheça a estrutura do nosso projeto

```
Labinho/
│
├── app/
│   ├── models/
│   │    └──models.py
│   ├── tabelas/
│   │    ├──cardapio.csv
│   │    └──users.csv
│   ├── templates/
│   ├── static/
│   │    ├── css/
│   │    ├── css_mobile/
│   │    ├── imagens/
│   │    └── javascript/
│   ├── __init__.py
│   ├── routes.py
│   └── alquimias.py
├── config.py
├── microblog.py
├── popular_db.py
└── requirements.txt
```

## Começando
Como abrir o nosso projeto na web

1. Baixe o repósitorio 'Labinho' completo
2. Navegue ao diretório do projeto no terminnal
3. Crie um ambiente virtual no diretório 'flask_env'
   ```
   python -m venv flask_env
   ```
4. Ative o ambiente
   ```
   flask_env\Scripts\activate
   ```
5. Baixe as bibliotecas
   ```
   pip install -r requirements.txt
   ```

## Configurações
Antes de prosseguir, é necessário configurar o Flask no terminal

1. No caminho raiz do projeto, no mesmo diretório que 'config.py', crie um arquivo chamado ".flaskenv" com sua chave secreta
   ```
   SECRET_KEY=3f9d0d8c17e544d99b27693d99fd845d
   ```
2. Agora, no terminal, ainda com o ambiente virtual ativado, digite os comandos para criar o banco de dados
   ```
   flask db init
   ```
   ```
   flask db migrate -m "Initial migration"
   ```
    ```
   flask db upgrade
   ```
   ```
   set FLASK_APP=app.py
   ```

## Popular o banco
Para ter uma experiência do site em funcionamento, popule o banco de dados para ter uma ideia de como ele ficaria em uma estrutura final hospedado em um servidor web

1. Execute popular_db.py no terminal
    ```
   python popular_db.py
   ```
## Processando
Para finalizar, ative o flask para carregar o servidor web em sua máquina

1. No terminal, digite:
    ```
    flask run
    ```
    
Aproveite o site!

## 👨‍💻 Desenvolvedores
Membros do grupo responsáveis pela criação do projeto







      
