/* Fecha a aba depois do desligamento.
 *
 * `window.close()` só funciona em janela que foi aberta por script — numa aba que o
 * usuário abriu, o navegador ignora em silêncio. Por isso a tela já diz que a aba pode
 * ser fechada, e aqui a gente apenas tenta; o texto é o caminho que sempre funciona. */
window.close();
