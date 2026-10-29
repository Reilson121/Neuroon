# Cadastro e gerenciamento de usuários

Na tela de entrada, **Criar uma conta** cadastra um estudante. Após o cadastro, entre com o email e a senha definidos. O cadastro não concede acesso administrativo, mesmo que um perfil seja enviado manualmente na requisição.

Administradores têm a opção **Usuários** na navegação, com listagem paginada (10 contas por página), cadastro, consulta, edição e exclusão de estudantes. Na edição, uma senha vazia mantém a senha atual. Contas administrativas aparecem para consulta e são protegidas contra edição e exclusão neste CRUD. Visitantes temporários não aparecem.

A exclusão é lógica: a conta fica inativa, perde o acesso inclusive em sessões abertas e deixa de aparecer na listagem. As conversas e avaliações permanecem vinculadas ao registro. O email continua reservado para preservar a identidade da conta excluída.

Se o administrador alterar o email de um estudante, o estudante precisa entrar novamente com o novo endereço. A sessão é vinculada ao identificador da conta e não pode assumir outra conta que venha a usar o endereço antigo.

## Integração

O CRUD usa a tabela `usuario` existente, o PostgreSQL, o Spring Security, o BCrypt e o cliente de API com cookies e CSRF já utilizados no projeto. Não exige novas dependências nem novas migrations. Nome e email são obrigatórios, com limites de 150 e 255 caracteres. O email é normalizado com remoção de espaços nas pontas e conversão para minúsculas; duplicidade retorna HTTP 409. Senhas novas exigem pelo menos 8 caracteres e no máximo 72 bytes em UTF-8, conforme o limite do BCrypt. Senhas e hashes não são devolvidos pela API.

| Método | Rota | Acesso |
| --- | --- | --- |
| POST | `/api/v1/auth/cadastro` | Público, com CSRF |
| GET | `/api/v1/admin/usuarios?pagina=0` | Administrador |
| GET | `/api/v1/admin/usuarios/{id}` | Administrador |
| POST | `/api/v1/admin/usuarios` | Administrador, com CSRF |
| PUT | `/api/v1/admin/usuarios/{id}` | Administrador, com CSRF |
| DELETE | `/api/v1/admin/usuarios/{id}` | Administrador, com CSRF |

POST e PUT recebem JSON com `nome`, `email` e `senha` (opcional no PUT). POST retorna 201, PUT retorna 200 e DELETE retorna 204. A listagem retorna `usuarios`, `pagina`, `totalPaginas` e `total`. O GET individual retorna 404 para contas inexistentes, excluídas ou de visitante.

Para criar o primeiro administrador, use as variáveis existentes `NEURON_BOOTSTRAP_ADMIN_EMAIL` e `NEURON_BOOTSTRAP_ADMIN_PASSWORD` ao iniciar o servidor. A senha inicial deve ter pelo menos 12 caracteres. Não coloque credenciais no código. A execução dos serviços e a configuração do banco continuam conforme o README.

## Verificação

Na pasta `frontend`: `npm.cmd test` e `npm.cmd run build`.

Na pasta `backend/demo`: `./gradlew.bat test` (ou selecione o JDK instalado com `-PjavaVersion=23`). Os testes `UsuarioApiTests` verificam cadastro, login, BCrypt, validação, duplicidade, permissões, CSRF, CRUD e bloqueio após exclusão. `Usuarios.test.jsx` verifica o cadastro pela tela de entrada e as ações de gerenciamento.
