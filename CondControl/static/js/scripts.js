$(document).ready(function() {
    // Função para formatar o valor em moeda
    function formatarMoeda(valor) {
        return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    }

    // Função para remover "R$" e converter para número, caso já venha formatado
    function limparValor(valor) {
        if (typeof valor === 'string') {
            return parseFloat(valor.replace(/[^\d,.-]/g, '').replace(',', '.'));
        }
        return valor;
    }

    // Função para buscar dados do servidor
    function buscarDados() {
        $.ajax({
            url: '/api/dados-financeiros',  // Altere para a sua rota que retorna os dados
            method: 'GET',
            success: function(data) {
                let totalReceitas = 0;
                let totalDespesas = 0;
                const transacoes = [];

                // Processa receitas
                data.receitas.forEach(function(receita) {
                    const valorLimpo = limparValor(receita.valor);  // Limpa o valor para remover duplicação de "R$"
                    totalReceitas += valorLimpo;
                    transacoes.push({
                        tipo: 'Receita',
                        descricao: receita.descricao,
                        valor: valorLimpo,
                        data: receita.data
                    });
                });

                // Processa despesas
                data.despesas.forEach(function(despesa) {
                    const valorLimpo = limparValor(despesa.valor);  // Limpa o valor para remover duplicação de "R$"
                    totalDespesas += valorLimpo;
                    transacoes.push({
                        tipo: 'Despesa',
                        descricao: despesa.descricao,
                        valor: valorLimpo,
                        data: despesa.data
                    });
                });

                // Atualiza totais
                $('#total-receitas').text(formatarMoeda(totalReceitas));  // Formata o valor total de receitas
                $('#total-despesas').text(formatarMoeda(totalDespesas));  // Formata o valor total de despesas

                // Preenche a tabela de transações
                transacoes.forEach(function(transacao) {
                    $('#transacoes-lista').append(`
                        <tr>
                            <td>${transacao.tipo}</td>
                            <td>${transacao.descricao}</td>
                            <td>${formatarMoeda(transacao.valor)}</td>
                            <td>${new Date(transacao.data).toLocaleDateString('pt-BR')}</td>
                        </tr>
                    `);
                });
            },
            error: function(error) {
                console.error('Erro ao buscar dados financeiros:', error);
            }
        });
    }

    // Chama a função ao carregar a página
    buscarDados();
});
