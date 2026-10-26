# Checklist de Contrato da API: UNB CORE

- [x] A API possui o prefixo versionado `/api/v1`.
- [x] A consulta de cursos, disciplinas e conteúdos é pública.
- [x] Os tipos de conteúdo aceitos estão definidos no contrato.
- [x] Cadastro, login e sessão não expõem senha.
- [x] Contribuições exigem autenticação.
- [x] `autor_id` e estado inicial são definidos pelo servidor.
- [x] Contribuições começam no estado `pendente`.
- [x] Moderadores e administradores podem decidir contribuições.
- [x] Aprovação sem `conteudo_id` cria conteúdo.
- [x] Aprovação com `conteudo_id` atualiza conteúdo.
- [x] Administração de usuários exige perfil `administrador`.
- [x] Erros possuem formato comum e códigos documentados.
- [x] O contrato não contém endpoints institucionais removidos do MVP.
