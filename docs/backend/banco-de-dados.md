# Modelo de dados e relações

Os modelos SQLModel que representam as tabelas ficam em
`backend/app/domain/models.py`. Os schemas HTTP não são tabelas: eles validam e
formatam os dados expostos pela API. Veja [Schemas da API](schemas.md).

## Entidades principais

- **`Usuario` (`usuario`)**: conta, perfil, estado ativo e campos de recuperação
  de senha.
- **`Curso` (`curso`)**: curso de graduação, com nome, sigla e grau.
- **`Disciplina` (`disciplina`)**: disciplina, código, nome, período e estado
  ativo.
- **`ConteudoAcademico` (`conteudoacademico`)**: conteúdo publicado, com tipo,
  título, corpo ou URL, disciplina, autor e estado.
- **`Contribuicao` (`contribuicao`)**: envio do autor para revisão, incluindo
  disciplina, conteúdo opcional relacionado, estado e dados de moderação.
- **`CursoDisciplina` (`curso_disciplina`)**: tabela de associação entre cursos
  e disciplinas.

## Relações entre as tabelas

| Relação | Chaves estrangeiras | Cardinalidade e significado |
|---|---|---|
| `Curso` ↔ `Disciplina` | `curso_disciplina.curso_id` → `curso.id`; `curso_disciplina.disciplina_id` → `disciplina.id` | Muitos-para-muitos: um curso tem várias disciplinas e a mesma disciplina pode pertencer a vários cursos. |
| `Disciplina` → `ConteudoAcademico` | `conteudoacademico.disciplina_id` → `disciplina.id` | Um-para-muitos: cada conteúdo publicado pertence a uma disciplina. |
| `Usuario` → `ConteudoAcademico` | `conteudoacademico.autor_id` → `usuario.id` | Um-para-muitos: cada conteúdo publicado tem um autor. |
| `Disciplina` → `Contribuicao` | `contribuicao.disciplina_id` → `disciplina.id` | Um-para-muitos: cada contribuição está vinculada a uma disciplina. |
| `Usuario` → `Contribuicao` | `contribuicao.autor_id` → `usuario.id` | Um-para-muitos: cada contribuição tem um autor. |
| `ConteudoAcademico` → `Contribuicao` | `contribuicao.conteudo_id` → `conteudoacademico.id` | Um-para-muitos opcional: uma contribuição pode propor alteração de conteúdo existente; `NULL` indica uma nova contribuição sem conteúdo publicado associado. |

## Relação muitos-para-muitos de curso e disciplina

Não há um único `curso_id` na tabela `disciplina`, pois uma disciplina pode ser
compartilhada por vários cursos. A associação é representada por uma linha em
`curso_disciplina` para cada par curso-disciplina:

```text
curso 1 ──< curso_disciplina >── 1 disciplina
```

`curso_disciplina` tem duas colunas:

- `curso_id`, chave estrangeira para `curso.id`;
- `disciplina_id`, chave estrangeira para `disciplina.id`.

As duas colunas formam juntas a chave primária composta `(curso_id,
disciplina_id)`, impedindo duplicar a mesma associação. Portanto, cada curso
pode aparecer em várias linhas e cada disciplina também pode aparecer em várias
linhas.

Na resposta da API, `DisciplinaPublica.curso_id` apresenta os IDs associados
como lista. A API consulta a tabela associativa para montar esse campo.

## Fluxo entre contribuição e conteúdo publicado

Uma contribuição nova começa sem `conteudo_id` e com estado `pendente`. Quando
aprovada, o serviço cria um registro em `conteudoacademico` e associa seu ID à
contribuição. Se a contribuição propõe alterações para um conteúdo existente,
ela referencia esse conteúdo; a aprovação atualiza o registro relacionado.

Assim, a contribuição mantém o histórico de autoria e moderação, enquanto
`ConteudoAcademico` é a entidade consultada para exibir material publicado.
