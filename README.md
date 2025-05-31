# Sistema de Autenticação com FastAPI

Este projeto é um sistema completo de autenticação e gestão de usuários construído com **FastAPI**, **SQLAlchemy** e **JWT**. Ele oferece:

- Cadastro com validação de senha forte
- Login e proteção de rotas via JWT
- Painel administrativo com controle de papéis (admin, editor, leitor)
- Redefinição de senha por e-mail
- Exclusão lógica de contas
- Controle de permissões seguro no back-end



## Tecnologias utilizadas

- **FastAPI** – Framework web moderno e performático
- **Uvicorn** – Servidor ASGI leve e rápido
- **SQLAlchemy** – ORM para comunicação com banco de dados
- **Passlib + Bcrypt** – Hash seguro de senhas
- **Jinja2** – Templates para e-mails
- **Python Multipart & Pydantic** – Suporte a formulários e validações
- **Itsdangerous** – Tokens seguros para redefinição de senha
- **Email-validator** – Validação de e-mail
- **Requests** – Chamadas HTTP externas (opcional)
- **JOSE** - Criptografia

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/ManuelaRiosSilva/sistema-autenticacao-usuarios.git
cd sistema-autenticacao-usuarios
````

### 2. (Opcional) Crie um ambiente virtual

```bash
python -m venv venv
venv\Scripts\activate          
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Execute o servidor

```bash
uvicorn main:app --reload
```

---

## Endpoints disponíveis

### Autenticação

| Método | Endpoint                   | Descrição                                 |
|--------|----------------------------|-------------------------------------------|
| POST   | `/usuarios/login`          | Autenticação de usuário e retorno do JWT  |
| GET    | `/usuarios/me`             | Dados do usuário logado                   |
| GET    | `/usuarios/rota_por_papel` | Redireciona o usuário para sua dashboard  |

---

### Gestão de usuário

| Método | Endpoint                    | Descrição                                     |
|--------|-----------------------------|-----------------------------------------------|
| POST   | `/usuarios/cadastro`        | Cadastro de novo usuário                      |
| DELETE | `/usuarios/excluir_conta`   | Desativa a conta do usuário autenticado       |
| GET    | `/usuarios/listar_todos`    | Listagem de todos os usuários (admin)         |
| POST   | `/usuarios/alterar_papel`   | Alteração de papel (admin -> editor/leitor)   |

---

### Recuperação de senha

| Método | Endpoint                   | Descrição                                   |
|--------|----------------------------|---------------------------------------------|
| POST   | `/usuarios/esqueci_senha`  | Envia e-mail com link de redefinição        |
| POST   | `/usuarios/trocar_senha`   | Altera a senha a partir de um token válido  |

---

## Regras de permissão

- Apenas usuários com papel **admin** podem alterar papéis de outros usuários
- Admins **não podem alterar o papel de outros admins**
- Admins **não podem promover outros usuários a admin**
- Cada papel tem sua dashboard:
  - `admin` → `/frontend/admin.html`
  - `editor` → `/frontend/editor.html`
  - `leitor` → `/frontend/leitor.html`

---

## Envio de e-mails

O envio de e-mails é feito por SMTP e é utilizado para redefinição de senha.

### Pré-requisitos

1. Ative a verificação em duas etapas na sua conta de e-mail (ex: Gmail)
2. Gere uma **senha de aplicativo**:
   - Acesse: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Configure em `utils/email.py`:

```python
SMTP_USER = "seu-email@gmail.com"
SMTP_PASSWORD = "senha-de-aplicativo-gerada"
```

Nunca use sua senha principal**. Sempre utilize uma senha de app.

---

## Estrutura sugerida

```
.
├── main.py
├── database.py
├── models.py
├── auth.py
├── utils/
│   ├── email.py
│   └── logs.py
├── routes/
│   └── usuarios.py
├── schemas/
│   └── ...
├── frontend/
│   ├── login.html
│   ├── cadastro.html
│   ├── admin.html
│   ├── editor.html
│   └── leitor.html
├── requirements.txt
└── README.md
```

---

## Telas prontas

- `login.html` – Tela de login
- `cadastro.html` – Tela de cadastro
- `admin.html` – Painel administrativo (gerencia papéis)
- `editor.html` – Área exclusiva para editores
- `leitor.html` – Área exclusiva para leitores

---

## Licença

Este projeto é open-source e pode ser adaptado livremente com os devidos créditos.

---

