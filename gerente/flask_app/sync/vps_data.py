"""Endpoints de dados VPS"""
from flask import Blueprint, jsonify, request
import os
import logging
from ..db import db

# Carregar variáveis de ambiente do .env
try:
    from gerente.env_loader import load_env
    load_env()
except ImportError:
    pass

logger = logging.getLogger(__name__)


def register_vps_data(bp: Blueprint):
    """Registra endpoints de dados VPS"""

    def _check_local_auth():
        local_pwd = os.getenv('LOCAL_API_PASSWORD', '').strip()
        if not local_pwd:
            return True
        provided = request.headers.get('X-Local-Auth') or request.headers.get('X-API-Password')
        return provided == local_pwd
    
    @bp.route("/dados/recentes", methods=["GET"])
    def vps_dados_recentes():
        """Lista dados mais recentes do VPS comparados com dados locais"""
        try:
            if not _check_local_auth():
                return jsonify({"success": False, "message": "Unauthorized"}), 401
            from gerente.vps_client import get_vps_client
            import hashlib
            import re
            
            def normalizar_id(texto):
                """Converte texto para formato de ID válido (substitui espaços por underscores)"""
                if not texto:
                    return texto
                return re.sub(r'\s+', '_', str(texto))
            
            def gerar_id_se_nulo_para_paciente(paciente):
                """Gera ID determinístico baseado em nome+unidade"""
                if paciente.get('id') and paciente['id'] != 'null':
                    return normalizar_id(paciente['id'])
                nome = None
                unidade = None
                if paciente.get('identificacao') and isinstance(paciente['identificacao'], dict):
                    nome = paciente['identificacao'].get('nome_gestante', '')
                    unidade = paciente['identificacao'].get('unidade_saude', '')
                if not nome:
                    nome = paciente.get('nome_gestante', 'desconhecido')
                if not unidade:
                    unidade = paciente.get('unidade_saude', '')
                # Gera hash determinístico
                chave = f"{nome.strip().lower()}_{unidade.strip().lower()}"
                hash_id = hashlib.md5(chave.encode()).hexdigest()[:8]
                return f"{normalizar_id(nome)}_{hash_id}"
            
            def gerar_id_se_nulo_para_agendamento(agendamento):
                """Gera ID determinístico para agendamento"""
                if agendamento.get('id') and agendamento['id'] != 'null':
                    return normalizar_id(agendamento['id'])
                # Gera hash baseado em data+hora+paciente_id
                data = agendamento.get('data_consulta', '')
                hora = agendamento.get('hora_consulta', '')
                pac_id = agendamento.get('paciente_id', '')
                chave = f"{pac_id}_{data}_{hora}"
                hash_id = hashlib.md5(chave.encode()).hexdigest()[:8]
                return f"agendamento_{hash_id}"
            
            vps_client = get_vps_client()
            if not vps_client:
                return jsonify({"success": False, "message": "Cliente VPS não disponível"}), 500
            
            logger.info("Buscando pacientes do VPS...")
            try:
                pacientes_vps = vps_client.get_pacientes_from_vps()
                # Gera IDs para pacientes sem ID
                for p in pacientes_vps:
                    if not p.get('id') or p['id'] == 'null':
                        p['id'] = gerar_id_se_nulo_para_paciente(p)
                logger.info(f"Pacientes VPS: {len(pacientes_vps)}")
            except Exception as e:
                logger.error(f"Erro ao buscar pacientes do VPS: {e}")
                pacientes_vps = []
            
            logger.info("Buscando agendamentos do VPS...")
            try:
                agendamentos_vps = vps_client.get_agendamentos_from_vps()
                # Gera IDs para agendamentos sem ID
                for a in agendamentos_vps:
                    if not a.get('id') or a['id'] == 'null':
                        a['id'] = gerar_id_se_nulo_para_agendamento(a)
                logger.info(f"Agendamentos VPS: {len(agendamentos_vps)}")
            except Exception as e:
                logger.error(f"Erro ao buscar agendamentos do VPS: {e}")
                agendamentos_vps = []
            
            pacientes_local = db.buscar_pacientes()
            agendamentos_local = db.listar_agendamentos()
            
            # Criar dicionários por ID E por nome+unidade
            pacientes_local_dict = {}
            pacientes_local_by_nome_unidade = {}
            for p_local in pacientes_local:
                pid = p_local.get('id')
                pid_norm = normalizar_id(pid) if pid else None
                if pid_norm:
                    pacientes_local_dict[pid_norm] = p_local
                # Indexar também por nome+unidade
                nome = p_local.get('identificacao', {}).get('nome_gestante', '').strip().lower()
                unidade = p_local.get('identificacao', {}).get('unidade_saude', '').strip().lower()
                if nome:
                    chave = f"{nome}_{unidade}"
                    pacientes_local_by_nome_unidade[chave] = p_local

            agendamentos_local_dict = {}
            for a_local in agendamentos_local:
                aid = a_local.get('id')
                aid_norm = normalizar_id(aid) if aid else None
                if aid_norm:
                    agendamentos_local_dict[aid_norm] = a_local
            
            pacientes_novos_vps = []
            pacientes_atualizados_vps = []
            pacientes_apenas_local = []
            
            # Remover duplicatas do VPS primeiro
            vps_unicos = {}
            for p_vps in pacientes_vps:
                nome = ''
                unidade = ''
                if p_vps.get('identificacao') and isinstance(p_vps['identificacao'], dict):
                    nome = p_vps['identificacao'].get('nome_gestante', '').strip().lower()
                    unidade = p_vps['identificacao'].get('unidade_saude', '').strip().lower()
                else:
                    nome = p_vps.get('nome_gestante', '').strip().lower()
                    unidade = p_vps.get('unidade_saude', '').strip().lower()
                chave = f"{nome}_{unidade}"
                # Manter apenas a versão mais recente
                if chave not in vps_unicos:
                    vps_unicos[chave] = p_vps
                else:
                    # Comparar timestamps
                    existente_mod = vps_unicos[chave].get('ultima_modificacao') or vps_unicos[chave].get('data_salvamento') or ''
                    novo_mod = p_vps.get('ultima_modificacao') or p_vps.get('data_salvamento') or ''
                    if novo_mod > existente_mod:
                        vps_unicos[chave] = p_vps
            
            for p_vps in vps_unicos.values():
                p_id_raw = p_vps.get('id')
                p_id = normalizar_id(p_id_raw) if p_id_raw else None
                
                # Tentar match por ID primeiro
                p_local = pacientes_local_dict.get(p_id) if p_id else None
                
                # Se não achou por ID, tentar por nome+unidade
                if not p_local:
                    nome = ''
                    unidade = ''
                    if p_vps.get('identificacao') and isinstance(p_vps['identificacao'], dict):
                        nome = p_vps['identificacao'].get('nome_gestante', '').strip().lower()
                        unidade = p_vps['identificacao'].get('unidade_saude', '').strip().lower()
                    else:
                        nome = p_vps.get('nome_gestante', '').strip().lower()
                        unidade = p_vps.get('unidade_saude', '').strip().lower()
                    if nome:
                        chave = f"{nome}_{unidade}"
                        p_local = pacientes_local_by_nome_unidade.get(chave)
                
                if not p_local:
                    # Não existe no BD local (nem por ID nem por nome+unidade)
                    pacientes_novos_vps.append(p_vps)
                    continue
                    
                # Existe localmente - adicionar como "atualizado" para permitir sincronização bidirecional
                # (enviar local→VPS ou baixar VPS→local)
                pacientes_atualizados_vps.append({
                    'vps': p_vps,
                    'local': p_local
                })
            
            vps_ids = {normalizar_id(p.get('id')) for p in pacientes_vps if p.get('id')}
            for p_local in pacientes_local:
                local_id_norm = normalizar_id(p_local.get('id')) if p_local.get('id') else None
                if not local_id_norm or local_id_norm not in vps_ids:
                    pacientes_apenas_local.append(p_local)
            
            agendamentos_novos_vps = []
            agendamentos_atualizados_vps = []
            agendamentos_apenas_local = []
            
            for a_vps in agendamentos_vps:
                a_id_raw = a_vps.get('id')
                a_id = normalizar_id(a_id_raw) if a_id_raw else None
                if not a_id or a_id not in agendamentos_local_dict:
                    # Não existe no BD local
                    agendamentos_novos_vps.append(a_vps)
                    continue
                a_local = agendamentos_local_dict[a_id]
                # Existe localmente - adicionar como "atualizado" para permitir sincronização bidirecional
                agendamentos_atualizados_vps.append({
                    'vps': a_vps,
                    'local': a_local
                })
            
            vps_agend_ids = {normalizar_id(a.get('id')) for a in agendamentos_vps if a.get('id')}
            for a_local in agendamentos_local:
                local_agend_id_norm = normalizar_id(a_local.get('id')) if a_local.get('id') else None
                if not local_agend_id_norm or local_agend_id_norm not in vps_agend_ids:
                    agendamentos_apenas_local.append(a_local)
            
            return jsonify({
                "success": True,
                "pacientes": {
                    "novos_vps": pacientes_novos_vps,
                    "atualizados_vps": pacientes_atualizados_vps,
                    "apenas_local": pacientes_apenas_local
                },
                "agendamentos": {
                    "novos_vps": agendamentos_novos_vps,
                    "atualizados_vps": agendamentos_atualizados_vps,
                    "apenas_local": agendamentos_apenas_local
                }
            })
        except Exception as e:
            import traceback
            return jsonify({"success": False, "message": "Erro ao buscar dados VPS"}), 500

    @bp.route("/dados/enviar", methods=["POST"])
    def vps_enviar_dados():
        """Envia dados selecionados para o VPS"""
        try:
            if not _check_local_auth():
                return jsonify({"success": False, "message": "Unauthorized"}), 401
            from gerente.vps_client import get_vps_client
            
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "message": "Dados não fornecidos"}), 400
            
            paciente_ids = data.get("paciente_ids", [])
            agendamento_ids = data.get("agendamento_ids", [])
            
            vps_client = get_vps_client()
            if not vps_client:
                return jsonify({"success": False, "message": "Cliente VPS não disponível"}), 500
            
            resultados = {
                "pacientes_enviados": 0,
                "agendamentos_enviados": 0,
                "erros": []
            }
            
            if paciente_ids:
                pacientes_para_enviar = []
                for pid in paciente_ids:
                    paciente = db.buscar_paciente(pid)
                    if paciente:
                        pacientes_para_enviar.append(paciente)
                
                if pacientes_para_enviar:
                    resultado = vps_client.sync_pacientes(pacientes_para_enviar)
                    if resultado.get('success'):
                        resultados["pacientes_enviados"] = len(pacientes_para_enviar)
                    else:
                        resultados["erros"].append(f"Erro ao enviar pacientes: {resultado.get('message')}")
            
            if agendamento_ids:
                agendamentos_para_enviar = []
                for aid in agendamento_ids:
                    agendamento = db.obter_agendamento(aid)
                    if agendamento:
                        agendamentos_para_enviar.append(agendamento)
                
                if agendamentos_para_enviar:
                    resultado = vps_client.sync_agendamentos(agendamentos_para_enviar)
                    if resultado.get('success'):
                        resultados["agendamentos_enviados"] = len(agendamentos_para_enviar)
                    else:
                        resultados["erros"].append(f"Erro ao enviar agendamentos: {resultado.get('message')}")
            
            return jsonify({
                "success": len(resultados["erros"]) == 0,
                "message": f"Enviados {resultados['pacientes_enviados']} pacientes e {resultados['agendamentos_enviados']} agendamentos",
                "resultados": resultados
            })
        except Exception as e:
            return jsonify({"success": False, "message": "Erro ao enviar dados"}), 500

    @bp.route("/dados/baixar", methods=["POST"])
    def vps_baixar_dados():
        """Baixa dados selecionados do VPS para o banco local"""
        import logging
        import re
        import hashlib
        logger = logging.getLogger(__name__)
        
        def normalizar_id(texto):
            """Converte texto para formato de ID válido (substitui espaços por underscores)"""
            if not texto:
                return texto
            return re.sub(r'\s+', '_', str(texto))
        
        def extrair_nome_unidade(paciente):
            """Extrai nome e unidade do paciente"""
            if not paciente:
                return None, None
            nome = None
            unidade = None
            if paciente.get('identificacao') and isinstance(paciente['identificacao'], dict):
                nome = paciente['identificacao'].get('nome_gestante', '').strip().lower()
                unidade = paciente['identificacao'].get('unidade_saude', '').strip().lower()
            if not nome:
                nome = paciente.get('nome_gestante', '').strip().lower()
            if not unidade:
                unidade = paciente.get('unidade_saude', '').strip().lower()
            return nome, unidade
        
        try:
            from gerente.vps_client import get_vps_client

            if not _check_local_auth():
                return jsonify({"success": False, "message": "Unauthorized"}), 401
            
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "message": "Dados não fornecidos"}), 400
            
            paciente_ids = data.get("paciente_ids", [])
            agendamento_ids = data.get("agendamento_ids", [])
            
            logger.info(f"Baixar VPS - Paciente IDs originais: {paciente_ids}")
            logger.info(f"Baixar VPS - Agendamento IDs originais: {agendamento_ids}")
            
            vps_client = get_vps_client()
            if not vps_client:
                return jsonify({"success": False, "message": "Cliente VPS não disponível"}), 500
            
            pacientes_vps = vps_client.get_pacientes_from_vps()
            agendamentos_vps = vps_client.get_agendamentos_from_vps()
            
            logger.info(f"Pacientes VPS encontrados: {len(pacientes_vps)}")
            
            # Buscar dados locais para matching
            pacientes_locais = db.buscar_pacientes(incluir_removidos=True)
            agendamentos_locais = db.listar_agendamentos()
            
            # Criar mapas locais por ID e por nome+unidade para matching
            pl_by_id = {normalizar_id(p.get('id')): p for p in pacientes_locais if p.get('id')}
            
            pl_by_nome_unidade = {}
            for p in pacientes_locais:
                nome, unidade = extrair_nome_unidade(p)
                if nome:
                    chave = f"{nome}_{unidade}"
                    pl_by_nome_unidade[chave] = p
            
            logger.info(f"Pacientes locais: {len(pacientes_locais)} | Mapa ID: {len(pl_by_id)} | Mapa Nome+Unidade: {len(pl_by_nome_unidade)}")
            
            al_by_id = {normalizar_id(a.get('id')): a for a in agendamentos_locais if a.get('id')}
            
            resultados = {
                "pacientes_baixados": 0,
                "pacientes_atualizados": 0,
                "agendamentos_baixados": 0,
                "agendamentos_atualizados": 0,
                "erros": []
            }
            
            # Processar pacientes
            for pid in paciente_ids:
                if pid == 'null' or not pid:
                    continue
                pid_normalizado = normalizar_id(pid)
                logger.info(f"Processando paciente ID: {pid_normalizado}")
                
                # Buscar paciente no VPS pelo ID fornecido
                paciente_vps = next((p for p in pacientes_vps if normalizar_id(p.get('id', '')) == pid_normalizado), None)
                
                if not paciente_vps:
                    logger.warning(f"Paciente {pid_normalizado} não encontrado no VPS")
                    resultados["erros"].append(f"Paciente {pid_normalizado} não encontrado no VPS")
                    continue
                
                # Tentar match local por nome+unidade (mais confiável que ID temporário)
                nome_vps, unidade_vps = extrair_nome_unidade(paciente_vps)
                chave_vps = f"{nome_vps}_{unidade_vps}" if nome_vps else None
                
                paciente_local = None
                id_local = None
                
                # Primeiro: tentar match por nome+unidade
                if chave_vps and chave_vps in pl_by_nome_unidade:
                    paciente_local = pl_by_nome_unidade[chave_vps]
                    id_local = paciente_local.get('id')
                    logger.info(f"Match por nome+unidade: {chave_vps} -> {id_local}")
                
                # Segundo: tentar match por ID normalizado
                if not paciente_local and pid_normalizado in pl_by_id:
                    paciente_local = pl_by_id[pid_normalizado]
                    id_local = paciente_local.get('id')
                    logger.info(f"Match por ID: {pid_normalizado}")
                
                # Se achou local, atualizar; senão, inserir novo
                if paciente_local:
                    try:
                        db.atualizar_paciente(id_local, paciente_vps)
                        resultados["pacientes_atualizados"] += 1
                        logger.info(f"Paciente {id_local} atualizado")
                    except Exception as e:
                        logger.error(f"Erro ao atualizar paciente {id_local}: {e}")
                        resultados["erros"].append(f"Erro ao atualizar paciente {id_local}: {str(e)}")
                else:
                    # Inserir novo paciente
                    try:
                        # Gerar ID determinístico se possível
                        if nome_vps and unidade_vps:
                            chave = f"{nome_vps}_{unidade_vps}"
                            hash_id = hashlib.md5(chave.encode()).hexdigest()[:8]
                            novo_id = f"{normalizar_id(nome_vps.title())}_{hash_id}"
                        else:
                            novo_id = pid_normalizado
                        
                        resultado = db.inserir_registro(
                            novo_id,
                            paciente_vps,
                            pc_id=paciente_vps.get('pc_id'),
                            ultima_modificacao=paciente_vps.get('ultima_modificacao'),
                            versao=paciente_vps.get('versao', 1),
                            status='ativo'
                        )
                        if resultado.get('success'):
                            resultados["pacientes_baixados"] += 1
                            logger.info(f"Paciente {novo_id} inserido (novo)")
                        else:
                            resultados["erros"].append(f"Erro ao inserir paciente: {resultado.get('message')}")
                    except Exception as e:
                        logger.error(f"Erro ao inserir paciente: {e}")
                        resultados["erros"].append(f"Erro ao inserir paciente: {str(e)}")
            
            # Processar agendamentos
            for aid in agendamento_ids:
                if aid == 'null' or not aid:
                    continue
                aid_normalizado = normalizar_id(aid)
                logger.info(f"Processando agendamento ID: {aid_normalizado}")
                
                # Tenta match por ID
                if aid_normalizado in al_by_id:
                    try:
                        agendamento_local = al_by_id[aid_normalizado]
                        # Buscar dados atualizados do VPS
                        agendamento_vps = next((a for a in agendamentos_vps if normalizar_id(a.get('id', '')) == aid_normalizado), None)
                        if agendamento_vps:
                            db.atualizar_agendamento(aid_normalizado, agendamento_vps)
                            resultados["agendamentos_atualizados"] += 1
                            logger.info(f"Agendamento {aid_normalizado} atualizado (match por ID)")
                    except Exception as e:
                        logger.error(f"Erro ao atualizar agendamento {aid_normalizado}: {e}")
                        resultados["erros"].append(f"Erro ao atualizar agendamento {aid_normalizado}: {str(e)}")
                    continue
                
                # Se não achou por ID, tenta inserir novo
                agendamento_vps = next((a for a in agendamentos_vps if normalizar_id(a.get('id', '')) == aid_normalizado), None)
                if agendamento_vps:
                    try:
                        resultado = db.criar_agendamento(
                            agendamento_id=aid_normalizado,
                            paciente_id=agendamento_vps.get('paciente_id'),
                            data_consulta=agendamento_vps.get('data_consulta'),
                            hora_consulta=agendamento_vps.get('hora_consulta'),
                            tipo_consulta=agendamento_vps.get('tipo_consulta'),
                            observacoes=agendamento_vps.get('observacoes'),
                            status=agendamento_vps.get('status', 'agendado')
                        )
                        if resultado.get('success'):
                            resultados["agendamentos_baixados"] += 1
                            logger.info(f"Agendamento {aid_normalizado} inserido (novo)")
                        else:
                            resultados["erros"].append(f"Erro ao inserir agendamento {aid_normalizado}: {resultado.get('message')}")
                    except Exception as e:
                        logger.error(f"Erro ao inserir agendamento {aid_normalizado}: {e}")
                        resultados["erros"].append(f"Erro ao inserir agendamento {aid_normalizado}: {str(e)}")
                else:
                    resultados["erros"].append(f"Agendamento {aid_normalizado} não encontrado no VPS")
            
            logger.info(f"Finalizado: {resultados}")
            return jsonify({
                "success": len(resultados["erros"]) == 0,
                "message": f"Baixados {resultados['pacientes_baixados']} pacientes, atualizados {resultados['pacientes_atualizados']}, baixados {resultados['agendamentos_baixados']} agendamentos, atualizados {resultados['agendamentos_atualizados']}",
                "resultados": resultados
            })
        except Exception as e:
            import traceback
            return jsonify({"success": False, "message": "Erro ao baixar dados"}), 500

    @bp.route("/dados/deletar", methods=["POST"])
    def vps_deletar_dados():
        """Deleta dados selecionados do VPS"""
        try:
            from gerente.vps_client import get_vps_client

            if not _check_local_auth():
                return jsonify({"success": False, "message": "Unauthorized"}), 401
            
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "message": "Dados não fornecidos"}), 400
            
            paciente_ids = data.get("paciente_ids", [])
            agendamento_ids = data.get("agendamento_ids", [])
            
            vps_client = get_vps_client()
            if not vps_client:
                return jsonify({"success": False, "message": "Cliente VPS não disponível"}), 500
            
            resultados = {
                "pacientes_deletados": 0,
                "agendamentos_deletados": 0,
                "erros": []
            }
            
            for pid in paciente_ids:
                try:
                    resultado = vps_client.delete_record('pacientes', pid)
                    if resultado.get('success'):
                        resultados["pacientes_deletados"] += 1
                    else:
                        resultados["erros"].append(f"Erro ao deletar paciente {pid}: {resultado.get('message')}")
                except Exception as e:
                    resultados["erros"].append(f"Erro ao deletar paciente {pid}: {str(e)}")
            
            for aid in agendamento_ids:
                try:
                    resultado = vps_client.delete_record('agendamentos', aid)
                    if resultado.get('success'):
                        resultados["agendamentos_deletados"] += 1
                    else:
                        resultados["erros"].append(f"Erro ao deletar agendamento {aid}: {resultado.get('message')}")
                except Exception as e:
                    resultados["erros"].append(f"Erro ao deletar agendamento {aid}: {str(e)}")
            
            return jsonify({
                "success": len(resultados["erros"]) == 0,
                "message": f"Deletados {resultados['pacientes_deletados']} pacientes e {resultados['agendamentos_deletados']} agendamentos do VPS",
                "resultados": resultados
            })
        except Exception as e:
            import traceback
            return jsonify({"success": False, "message": "Erro ao deletar dados"}), 500
