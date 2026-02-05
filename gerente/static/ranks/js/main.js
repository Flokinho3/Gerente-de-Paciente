(function () {
    'use strict';

    var comTrava = true;

    function configurarDropdowns() {
        var dropdowns = document.querySelectorAll('.topbar-dropdown');
        dropdowns.forEach(function (dropdown) {
            var btn = dropdown.querySelector('.topbar-dropdown-btn');
            if (!btn) return;
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                dropdowns.forEach(function (d) {
                    if (d !== dropdown) d.classList.remove('active');
                });
                dropdown.classList.toggle('active');
            });
        });
        document.addEventListener('click', function (e) {
            if (!e.target.closest('.topbar-dropdown')) {
                dropdowns.forEach(function (d) { d.classList.remove('active'); });
            }
        });
        document.querySelectorAll('.topbar-dropdown-item').forEach(function (item) {
            item.addEventListener('click', function () {
                dropdowns.forEach(function (d) { d.classList.remove('active'); });
            });
        });
    }

    function configurarInfoModal() {
        var btnInfo = document.getElementById('ranks-toggle-info');
        var overlay = document.getElementById('ranks-info-overlay');
        var modal = document.getElementById('ranks-info-modal');
        var body = document.getElementById('ranks-info-body');
        var closeBtn = document.getElementById('ranks-info-close');

        var conteudo = [
            '<h3>Como funciona o ranking das unidades</h3>',
            '<p>O ranking mostra quais unidades apresentam, de forma geral, os melhores resultados no acompanhamento das gestantes. Para isso, o sistema analisa 7 indicadores importantes do pré-natal e gera um score único para cada unidade.</p>',
            '<p>O score representa uma média dos resultados positivos nesses indicadores. Quanto maior o score, melhor o desempenho geral da unidade.</p>',
            '<h3>Indicadores avaliados</h3>',
            '<ul>',
            '<li>Início do pré-natal antes de 12 semanas</li>',
            '<li>Realização de 6 ou mais consultas</li>',
            '<li>Vacinas em dia</li>',
            '<li>Plano de parto registrado</li>',
            '<li>Participação em grupos</li>',
            '<li>Acesso ao Bolsa Família</li>',
            '<li>Vacina contra COVID-19</li>',
            '</ul>',
            '<h3>Regras para participação no ranking</h3>',
            '<p>Para garantir um ranking justo, só participam unidades que tenham um volume mínimo de dados confiáveis. A unidade entra no ranking se atender a <strong>pelo menos uma</strong> das condições abaixo:</p>',
            '<ul>',
            '<li>Ter 50 ou mais gestantes acompanhadas, ou</li>',
            '<li>Ter 70% ou mais dos prontuários completos nos indicadores avaliados</li>',
            '</ul>',
            '<h3>Regras para o 1º lugar (unidade em destaque)</h3>',
            '<p>Para ser considerada Unidade em Destaque, além de um bom score geral, a unidade precisa apresentar um desempenho mínimo nos indicadores mais críticos do cuidado pré-natal.</p>',
            '<p>Os critérios mínimos são:</p>',
            '<ul>',
            '<li>Início do pré-natal antes de 12 semanas: 40% ou mais</li>',
            '<li>6 ou mais consultas realizadas: 50% ou mais</li>',
            '<li>Vacinas completas: 60% ou mais</li>',
            '</ul>',
            '<p>Unidades que não atingem esses mínimos continuam aparecendo no ranking, mas não são elegíveis ao 1º lugar.</p>',
            '<h3>Importante saber</h3>',
            '<ul>',
            '<li>Alguns indicadores têm peso maior no cálculo do score, por refletirem etapas mais essenciais do cuidado pré-natal.</li>',
            '<li>Quando há muitos prontuários sem informação registrada, o score pode ser reduzido, reforçando a importância do registro correto.</li>',
            '<li>Em caso de empate no score, a unidade com maior número de gestantes acompanhadas aparece melhor posicionada.</li>',
            '</ul>'
        ].join('');

        function abrir() {
            if (body) body.innerHTML = conteudo;
            if (overlay) {
                overlay.classList.add('active');
                overlay.setAttribute('aria-hidden', 'false');
            }
            if (closeBtn) closeBtn.focus();
        }

        function fechar() {
            if (overlay) {
                overlay.classList.remove('active');
                overlay.setAttribute('aria-hidden', 'true');
            }
        }

        if (btnInfo) btnInfo.addEventListener('click', abrir);
        if (closeBtn) closeBtn.addEventListener('click', fechar);
        if (overlay) {
            overlay.addEventListener('click', function (e) {
                if (e.target === overlay) fechar();
            });
        }
        if (modal) {
            modal.addEventListener('click', function (e) { e.stopPropagation(); });
        }
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && overlay && overlay.classList.contains('active')) fechar();
        });
    }

    function configurarToggleTrava() {
        var btnCom = document.getElementById('ranks-toggle-com-trava');
        var btnSem = document.getElementById('ranks-toggle-sem-trava');
        var hint = document.getElementById('ranks-toggle-hint');
        var legend = document.getElementById('ranks-legend');
        var desc = document.getElementById('ranks-destaque-desc');

        function atualizarLegenda() {
            if (legend) {
                legend.textContent = comTrava
                    ? 'Score = média ponderada. Travas: amostra mínima (≥50 pacientes ou ≥70% prontuários completos), pisos (início <12 sem. ≥40%, ≥6 consultas ≥50%, vacinas ≥60%), pesos, penalidade −5% se >20% dados ausentes em algum critério.'
                    : 'Score = média dos percentuais positivos em: início pré-natal <12 sem., ≥6 consultas, vacinas, plano de parto, grupos, Bolsa Família, vacina COVID.';
            }
            if (desc) {
                desc.textContent = comTrava
                    ? 'Unidade em destaque: 1º lugar entre as elegíveis (atingem pisos mínimos). Score com pesos e penalidades.'
                    : 'A unidade em que a maioria dos pacientes possui os melhores resultados (média dos indicadores).';
            }
            if (hint) {
                hint.textContent = comTrava
                    ? 'Padrão: com travas (amostra mínima, pisos, pesos, penalidade por dado ausente).'
                    : 'Ranking simples: média dos indicadores, todas as unidades, sem restrições.';
            }
        }

        function setActive(btn) {
            if (btnCom) btnCom.classList.remove('active');
            if (btnSem) btnSem.classList.remove('active');
            if (btn) btn.classList.add('active');
        }

        if (btnCom) {
            btnCom.addEventListener('click', function () {
                if (comTrava) return;
                comTrava = true;
                setActive(btnCom);
                atualizarLegenda();
                carregarRanking();
            });
        }
        if (btnSem) {
            btnSem.addEventListener('click', function () {
                if (!comTrava) return;
                comTrava = false;
                setActive(btnSem);
                atualizarLegenda();
                carregarRanking();
            });
        }
        atualizarLegenda();
    }

    function renderDestaque(data) {
        var placeholder = document.getElementById('ranks-destaque-placeholder');
        var content = document.getElementById('ranks-destaque-content');
        var empty = document.getElementById('ranks-destaque-empty');
        if (!placeholder || !content || !empty) return;

        placeholder.style.display = 'none';
        content.style.display = 'none';
        empty.style.display = 'none';

        if (!data || !data.unidade_destaque) {
            empty.style.display = 'block';
            if (data && data.com_trava && data.ranking_geral && data.ranking_geral.length > 0) {
                empty.textContent = 'Nenhuma unidade elegível ao 1º lugar (todas abaixo dos pisos mínimos).';
            } else {
                empty.textContent = 'Nenhuma unidade com pacientes cadastrados.';
            }
            return;
        }

        var d = data.unidade_destaque;
        var nomeEl = document.getElementById('ranks-destaque-nome');
        var scoreEl = document.getElementById('ranks-destaque-score');
        var totalEl = document.getElementById('ranks-destaque-total');
        if (nomeEl) nomeEl.textContent = d.unidade;
        if (scoreEl) scoreEl.textContent = 'Score ' + d.score + '%';
        if (totalEl) totalEl.textContent = d.total;
        content.style.display = 'block';
    }

    function renderTabela(data) {
        var tbody = document.getElementById('ranks-tabela-body');
        if (!tbody) return;
        tbody.innerHTML = '';

        var list = (data && data.ranking_geral) ? data.ranking_geral : [];
        var comTravaAtual = !!(data && data.com_trava);
        list.forEach(function (r) {
            var tr = document.createElement('tr');
            var posClass = r.posicao <= 3 ? ' ranks-pos-' + r.posicao : '';
            tr.className = posClass;
            var naoElegivel = comTravaAtual && r.elegivel_1o_lugar === false;
            var unidadeHtml = escapeHtml(r.unidade);
            if (naoElegivel) {
                unidadeHtml += ' <span class="ranks-nao-elegivel" title="Não atingiu pisos mínimos em algum critério essencial">(não elegível ao 1º)</span>';
            }
            tr.innerHTML =
                '<td class="ranks-col-pos">' + r.posicao + '</td>' +
                '<td class="ranks-col-unidade">' + unidadeHtml + '</td>' +
                '<td class="ranks-col-score">' + r.score + '%</td>' +
                '<td class="ranks-col-total">' + r.total + '</td>';
            tbody.appendChild(tr);
        });
    }

    function escapeHtml(s) {
        if (!s) return '';
        var div = document.createElement('div');
        div.textContent = s;
        return div.innerHTML;
    }

    function carregarRanking() {
        var placeholder = document.getElementById('ranks-destaque-placeholder');
        if (placeholder) {
            placeholder.textContent = 'Carregando…';
            placeholder.style.display = 'block';
        }
        var content = document.getElementById('ranks-destaque-content');
        var empty = document.getElementById('ranks-destaque-empty');
        if (content) content.style.display = 'none';
        if (empty) empty.style.display = 'none';

        var url = '/api/ranking_unidades_geral?trava=' + (comTrava ? '1' : '0');
        fetch(url)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (placeholder) placeholder.style.display = 'none';
                renderDestaque(data);
                renderTabela(data);
            })
            .catch(function (e) {
                if (placeholder) {
                    placeholder.textContent = 'Erro ao carregar ranking. Tente recarregar.';
                    placeholder.style.display = 'block';
                }
                renderTabela({ ranking_geral: [] });
            });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            configurarDropdowns();
            configurarToggleTrava();
            configurarInfoModal();
            carregarRanking();
        });
    } else {
        configurarDropdowns();
        configurarToggleTrava();
        configurarInfoModal();
        carregarRanking();
    }
})();
