import { useEffect, useState } from 'react'
import { api, ApiError } from '../services/api'
import { useAuth } from '../state/auth'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/ui/EmptyState'
import Button from '../components/ui/Button'
import PageLayout, { AsideCard } from '../components/layout/PageLayout'
import { formatarData } from '../components/conteudos/formatacao'
import './MinhasContribuicoesPage.css'
import './ContribuicaoPage.css'
import './governance.css'

const PERFIS = { usuario: 'Usuário', moderador: 'Moderador', administrador: 'Administrador' }
const FORMULARIO_VAZIO = { nome: '', email: '', senha: '', perfil: 'moderador' }

function mensagem(requestError, padrao) {
  return requestError instanceof ApiError ? requestError.message : padrao
}

function montarConsulta({ aba, busca, perfil, situacao }) {
  const params = new URLSearchParams()
  if (aba === 'equipe') params.set('perfil', 'equipe')
  else if (perfil) params.set('perfil', perfil)
  if (busca.trim()) params.set('busca', busca.trim())
  if (situacao) params.set('ativo', situacao === 'ativos' ? 'true' : 'false')
  const texto = params.toString()
  return `/usuarios/gestao${texto ? `?${texto}` : ''}`
}

function AdminUsuariosPage({ onNavigate }) {
  const { user, isAuthenticated } = useAuth()
  const isAdmin = user?.perfil === 'administrador'
  const canManage = isAuthenticated && ['moderador', 'administrador'].includes(user?.perfil)

  const [aba, setAba] = useState(isAdmin ? 'equipe' : 'todos')
  const [busca, setBusca] = useState('')
  const [perfil, setPerfil] = useState('')
  const [situacao, setSituacao] = useState('')
  const [users, setUsers] = useState([])
  const [isLoading, setIsLoading] = useState(canManage)
  const [error, setError] = useState(null)
  const [aviso, setAviso] = useState('')
  const [form, setForm] = useState(FORMULARIO_VAZIO)
  const [senhaPara, setSenhaPara] = useState(null)
  const [novaSenha, setNovaSenha] = useState('')
  const [recarregar, setRecarregar] = useState(0)

  // Sem sessão (por exemplo, depois que ela expira), leva ao login como as outras páginas protegidas.
  useEffect(() => {
    if (!isAuthenticated) onNavigate?.('/login')
  }, [isAuthenticated, onNavigate])

  useEffect(() => {
    if (!canManage) return undefined

    const controller = new AbortController()
    // Espera a pessoa parar de digitar antes de buscar.
    const timer = setTimeout(() => {
      setIsLoading(true)
      api.get(montarConsulta({ aba, busca, perfil, situacao }), { signal: controller.signal })
        .then((response) => setUsers(Array.isArray(response) ? response : []))
        .catch((requestError) => {
          if (requestError.name !== 'AbortError') setError(mensagem(requestError, 'Não foi possível carregar os usuários.'))
        })
        .finally(() => {
          if (!controller.signal.aborted) setIsLoading(false)
        })
    }, 250)

    return () => {
      clearTimeout(timer)
      controller.abort()
    }
  }, [canManage, aba, busca, perfil, situacao, recarregar])

  async function executar(acao, sucesso) {
    setError(null)
    setAviso('')
    try {
      await acao()
      setAviso(sucesso)
      setRecarregar((valor) => valor + 1)
      return true
    } catch (requestError) {
      setError(mensagem(requestError, 'Não foi possível concluir a ação.'))
      return false
    }
  }

  async function createUser(event) {
    event.preventDefault()
    const ok = await executar(() => api.post('/usuarios', form), `Conta de ${form.nome} criada.`)
    if (ok) setForm(FORMULARIO_VAZIO)
  }

  function alternarSituacao(usuario) {
    const ativo = !usuario.ativo
    executar(
      () => api.patch(`/usuarios/${usuario.id}/situacao`, { ativo }),
      `${usuario.nome} foi ${ativo ? 'reativado' : 'desativado'}.`,
    )
  }

  function mudarPerfil(usuario, novoPerfil) {
    executar(
      () => api.patch(`/usuarios/${usuario.id}`, { perfil: novoPerfil }),
      `${usuario.nome} agora é ${PERFIS[novoPerfil].toLowerCase()}.`,
    )
  }

  function excluir(usuario) {
    const confirmado = window.confirm(
      `Excluir a conta de ${usuario.nome} de vez?\n\n`
      + 'A conta e os dados pessoais serão apagados, junto com as contribuições dela. '
      + 'Os conteúdos já publicados continuam na base com o autor "Usuário removido". Não dá para desfazer.',
    )
    if (confirmado) executar(() => api.delete(`/usuarios/${usuario.id}`), `A conta de ${usuario.nome} foi excluída.`)
  }

  async function definirSenha(event, usuario) {
    event.preventDefault()
    if (novaSenha.length < 8) {
      setError('A senha temporária precisa ter pelo menos 8 caracteres.')
      return
    }
    const ok = await executar(
      () => api.post(`/usuarios/${usuario.id}/senha-temporaria`, { nova_senha: novaSenha }),
      `Senha temporária definida para ${usuario.nome}. Passe a senha para a pessoa e peça que ela troque em Meu perfil.`,
    )
    if (ok) {
      setSenhaPara(null)
      setNovaSenha('')
    }
  }

  const cabecalho = {
    onNavigate,
    eyebrow: isAdmin ? 'Administração' : 'Moderação',
    title: 'Usuários',
    description: isAdmin
      ? 'Gerencie a equipe (moderadores e administradores) e as contas de todos os usuários.'
      : 'Gerencie as contas de usuários comuns: desative, reative ou exclua quando necessário.',
  }

  if (!canManage) {
    return (
      <PageLayout {...cabecalho} title="Usuários" width="narrow">
        <EmptyState title="Acesso restrito">Somente moderadores e administradores podem acessar esta área.</EmptyState>
      </PageLayout>
    )
  }

  const aside = aba === 'equipe' ? (
    <AsideCard title="Novo membro da equipe">
      <form className="contribution-form" onSubmit={createUser}>
        <label>Nome<input value={form.nome} onChange={(event) => setForm({ ...form, nome: event.target.value })} required /></label>
        <label>E-mail<input type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} required /></label>
        <label>Senha inicial<input type="password" value={form.senha} onChange={(event) => setForm({ ...form, senha: event.target.value })} minLength="8" required /></label>
        <label>Perfil<select value={form.perfil} onChange={(event) => setForm({ ...form, perfil: event.target.value })}><option value="moderador">Moderador</option><option value="administrador">Administrador</option></select></label>
        <Button type="submit">Criar conta</Button>
      </form>
    </AsideCard>
  ) : (
    <AsideCard title="Privacidade e permissões">
      <ul>
        <li>Ninguém vê a senha de outra pessoa.</li>
        {isAdmin
          ? <li>Administradores podem mudar o perfil e definir uma senha temporária para quem esqueceu a senha.</li>
          : <li>Moderadores veem só usuários comuns, sem o e-mail, e não alteram dados da conta.</li>}
        <li>Excluir apaga a conta e as contribuições; os conteúdos publicados ficam como “Usuário removido”.</li>
      </ul>
    </AsideCard>
  )

  return (
    <PageLayout {...cabecalho} aside={aside} asideLabel={aba === 'equipe' ? 'Criar conta da equipe' : 'Privacidade e permissões'}>
      {isAdmin && (
        <div className="governance-tabs" role="tablist" aria-label="Grupo de contas">
          {[{ valor: 'equipe', rotulo: 'Equipe' }, { valor: 'todos', rotulo: 'Todos os usuários' }].map((item) => (
            <button
              key={item.valor}
              type="button"
              role="tab"
              aria-selected={aba === item.valor}
              className={`governance-tab ${aba === item.valor ? 'governance-tab--active' : ''}`}
              onClick={() => { setAba(item.valor); setAviso(''); setError(null) }}
            >
              {item.rotulo}
            </button>
          ))}
        </div>
      )}

      {aba === 'todos' && (
        <div className="contribution-form users-filters">
          <div className="contribution-form__grid">
            <label>Buscar<input type="search" value={busca} onChange={(event) => setBusca(event.target.value)} placeholder={isAdmin ? 'Nome ou e-mail' : 'Nome'} /></label>
            <label>Situação<select value={situacao} onChange={(event) => setSituacao(event.target.value)}><option value="">Todas</option><option value="ativos">Ativos</option><option value="desativados">Desativados</option></select></label>
            {isAdmin && (
              <label>Perfil<select value={perfil} onChange={(event) => setPerfil(event.target.value)}><option value="">Todos</option><option value="usuario">Usuários</option><option value="moderador">Moderadores</option><option value="administrador">Administradores</option></select></label>
            )}
          </div>
        </div>
      )}

      {error && <ErrorMessage>{error}</ErrorMessage>}
      {aviso && <p className="content-page__feedback" role="status">{aviso}</p>}
      {isLoading && users.length === 0 && <p className="page-status">Carregando usuários...</p>}
      {!isLoading && users.length === 0 && <EmptyState title="Nenhuma conta encontrada">Tente outra busca ou filtro.</EmptyState>}

      {users.length > 0 && (
        <section className="my-contributions-list" aria-label="Contas" aria-busy={isLoading}>
          {users.map((usuario) => {
            const isOwnAccount = user?.id != null && usuario.id === user.id
            return (
              <article className="my-contribution-card" key={usuario.id}>
                <div className="my-contribution-card__heading">
                  <span className="badge badge-category">{PERFIS[usuario.perfil] || usuario.perfil}</span>
                  <span className={`badge ${usuario.ativo ? 'badge-aprovada' : 'badge-arquivada'}`}>{usuario.ativo ? 'Ativa' : 'Desativada'}</span>
                </div>
                <h2>{usuario.nome}{isOwnAccount ? ' (você)' : ''}</h2>
                <p className="moderation-card__meta">
                  {usuario.email ? `${usuario.email} · ` : ''}Cadastro em {formatarData(usuario.criado_em, 'medium')} · {usuario.total_contribuicoes} {usuario.total_contribuicoes === 1 ? 'contribuição' : 'contribuições'}
                </p>

                {isOwnAccount ? (
                  <p className="my-contribution-card__note">Esta é a sua conta. Para alterar seus dados, use Meu perfil.</p>
                ) : (
                  <>
                    <span className="my-contribution-card__actions">
                      <Button variant="outline" onClick={() => alternarSituacao(usuario)}>{usuario.ativo ? 'Desativar' : 'Reativar'}</Button>
                      {isAdmin && (
                        <label className="users-role">
                          <span className="visually-hidden">Perfil de {usuario.nome}</span>
                          <select value={usuario.perfil} onChange={(event) => mudarPerfil(usuario, event.target.value)} aria-label={`Perfil de ${usuario.nome}`}>
                            <option value="usuario">Usuário</option>
                            <option value="moderador">Moderador</option>
                            <option value="administrador">Administrador</option>
                          </select>
                        </label>
                      )}
                      {isAdmin && senhaPara !== usuario.id && (
                        <Button variant="outline" onClick={() => { setSenhaPara(usuario.id); setNovaSenha('') }}>Senha temporária</Button>
                      )}
                      <Button variant="danger" onClick={() => excluir(usuario)}>Excluir conta</Button>
                    </span>
                    {isAdmin && senhaPara === usuario.id && (
                      <form className="contribution-form" onSubmit={(event) => definirSenha(event, usuario)} noValidate>
                        <label>
                          Nova senha temporária para {usuario.nome}
                          <input type="password" value={novaSenha} onChange={(event) => setNovaSenha(event.target.value)} minLength="8" autoComplete="new-password" />
                          <span className="contribution-form__hint">A senha atual não é exibida. Passe a nova para a pessoa e peça que ela troque em Meu perfil.</span>
                        </label>
                        <span className="my-contribution-card__actions">
                          <Button variant="outline" onClick={() => setSenhaPara(null)}>Cancelar</Button>
                          <Button type="submit">Definir senha</Button>
                        </span>
                      </form>
                    )}
                  </>
                )}
              </article>
            )
          })}
        </section>
      )}
    </PageLayout>
  )
}

export default AdminUsuariosPage
