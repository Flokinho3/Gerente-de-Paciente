"""Endpoints de dados VPS"""
from flask import Blueprint, jsonify, request
import os
import logging
from ..db import db

logger = logging.getLogger(__name__)


def register_vps_data(bp: Blueprint):
    """Registra endpoints de dados VPS"""
    
    @bp.route("/dados/recentes", methods=["GET"])
    def vps_dados_recentes():
        """Lista dados mais recentes do VPS comparados com dados locais"""
        try:
            from gerente.vps_client import get_vps_client
            import uuid
            import re
            
            def normalizar_id(texto):
                """Converte texto para formato de ID válido (substitui espaços por underscores)"""
                if not texto:
                    return texto
                return re.sub(r'\s+', '_', str(texto))
            
            def gerar_id_se_nulo_para_paciente(paciente):
                """Gera ID se for nulo"""
                if paciente.get('id') and paciente['id'] != 'null':
                    return normalizar_id(paciente['id'])
                nome = None
                if paciente.get('identificacao') and isinstance(paciente['identificacao'], dict):
                    nome = paciente['identificacao'].get('nome_gestante')
                if not nome:
                    nome = paciente.get('nome_gestante', 'desconhecido')
                return f"{normalizar_id(nome)}_{uuid.uuid4().hex[:8]}"
            
            def gerar_id_se_nulo_para_agendamento(agendamento):
                """Gera ID para agendamento se for nulo"""
                if agendamento.get('id') and agendamento['id'] != 'null':
                    return normalizar_id(agendamento['id'])
                return f"agendamento_{uuid.uuid4().hex[:8]}"
            
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
            
            pacientes_local_dict = {p['id']: p for p in pacientes_local}
            agendamentos_local_dict = {a['id']: a for a in agendamentos_local}
            
            pacientes_novos_vps = []
            pacientes_atualizados_vps = []
            pacientes_apenas_local = []
            
            for p_vps in pacientes_vps:
                p_id = p_vps.get('id')
                if p_id not in pacientes_local_dict:
                    pacientes_novos_vps.append(p_vps)
                else:
                    p_local = pacientes_local_dict[p_id]
                    vps_mod = (p_vps.get('ultima_modificacao') or '') or (p_vps.get('data_salvamento') or '')
                    local_mod = (p_local.get('ultima_modificacao') or '') or (p_local.get('data_salvamento') or '')
                    if vps_mod and local_mod and vps_mod > local_mod:
                        pacientes_atualizados_vps.append({
                            'vps': p_vps,
                            'local': p_local
                        })
            
            vps_ids = {p.get('id') for p in pacientes_vps}
            for p_local in pacientes_local:
                if p_local['id'] not in vps_ids:
                    pacientes_apenas_local.append(p_local)
            
            agendamentos_novos_vps = []
            agendamentos_atualizados_vps = []
            agendamentos_apenas_local = []
            
            for a_vps in agendamentos_vps:
                a_id = a_vps.get('id')
                if a_id not in agendamentos_local_dict:
                    agendamentos_novos_vps.append(a_vps)
                else:
                    a_local = agendamentos_local_dict[a_id]
                    vps_mod = (a_vps.get('ultima_modificacao') or '') or (a_vps.get('data_atualizacao') or '')
                    local_mod = (a_local.get('ultima_modificacao') or '') or (a_local.get('data_atualizacao') or '')
                    if vps_mod and local_mod and vps_mod > local_mod:
                        agendamentos_atualizados_vps.append({
                            'vps': a_vps,
                            'local': a_local
                        })
            
            vps_agend_ids = {a.get('id') for a in agendamentos_vps}
            for a_local in agendamentos_local:
                if a_local['id'] not in vps_agend_ids:
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
            return jsonify({"success": False, "message": str(e), "traceback": traceback.format_exc()}), 500

    @bp.route("/dados/enviar", methods=["POST"])
    def vps_enviar_dados():
        """Envia dados selecionados para o VPS"""
        try:
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
            import traceback
            return jsonify({"success": False, "message": str(e), "traceback": traceback.format_exc()}), 500

    @bp.route("/dados/baixar", methods=["POST"])
    def vps_baixar_dados():
        """Baixa dados selecionados do VPS para o banco local"""
        import logging
        import re
        import uuid
        logger = logging.getLogger(__name__)
        
        def normalizar_id(texto):
            """Converte texto para formato de ID válido (substitui espaços por underscores)"""
            if not texto:
                return texto
            return re.sub(r'\s+', '_', str(texto))
        
        def extrair_nome_paciente(paciente):
            """Extrai nome do paciente de forma consistente"""
            if not paciente:
                return None
            nome = None
            if paciente.get('identificacao') and isinstance(paciente['identificacao'], dict):
                nome = paciente['identificacao'].get('nome_gestante')
            if not nome:
                nome = paciente.get('nome_gestante')
            if nome:
                return normalizar_id(nome.strip())
            return None
        
        try:
            from gerente.vps_client import get_vps_client
            
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
            
            # Criar mapas locais por ID e por Nome para matching
            pl_by_id = {p.get('id'): p for p in pacientes_locais if p.get('id')}
            
            pl_by_nome = {}
            for p in pacientes_locais:
                nome = extrair_nome_paciente(p)
                if nome:
                    pl_by_nome[nome] = p
            
            logger.info(f"Pacientes locais: {len(pacientes_locais)} | Mapa ID: {len(pl_by_id)} | Mapa Nome: {len(pl_by_nome)}")
            
            al_by_id = {a.get('id'): a for a in agendamentos_locais if a.get('id')}
            
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
                
                # Primeiro tenta match por ID
                if pid_normalizado in pl_by_id:
                    try:
                        paciente_local = pl_by_id[pid_normalizado]
                        # Buscar dados atualizados do VPS
                        paciente_vps = next((p for p in pacientes_vps if normalizar_id(p.get('id', '')) == pid_normalizado), None)
                        if paciente_vps:
                            db.atualizar_paciente(pid_normalizado, paciente_vps)
                            resultados["pacientes_atualizados"] += 1
                            logger.info(f"Paciente {pid_normalizado} atualizado (match por ID)")
                    except Exception as e:
                        logger.error(f"Erro ao atualizar paciente {pid_normalizado}: {e}")
                        resultados["erros"].append(f"Erro ao atualizar paciente {pid_normalizado}: {str(e)}")
                    continue
                
                # Se não achou por ID direto, tenta match por Nome (para IDs gerados temporariamente)
                paciente_vps = None
                paciente_vps_encontrado = False
                
                # Primeiro tenta match por ID exato no VPS
                paciente_vps = next((p for p in pacientes_vps if normalizar_id(p.get('id', '')) == pid_normalizado), None)
                
                if paciente_vps:
                    # Achou por ID, agora tenta match por nome no local
                    nome_vps = extrair_nome_paciente(paciente_vps)
                    if nome_vps and nome_vps in pl_by_nome:
                        paciente_local = pl_by_nome[nome_vps]
                        id_local = paciente_local.get('id')
                        try:
                            db.atualizar_paciente(id_local, paciente_vps)
                            resultados["pacientes_atualizados"] += 1
                            logger.info(f"Paciente {nome_vps} atualizado usando ID local {id_local} (match por Nome)")
                            paciente_vps_encontrado = True
                        except Exception as e:
                            logger.error(f"Erro ao atualizar paciente por nome {nome_vps}: {e}")
                            resultados["erros"].append(f"Erro ao atualizar paciente {nome_vps}: {str(e)}")
                    else:
                        # Não achou por nome, insere novo
                        try:
                            resultado = db.inserir_registro(
                                pid_normalizado,
                                paciente_vps,
                                pc_id=paciente_vps.get('pc_id'),
                                ultima_modificacao=paciente_vps.get('ultima_modificacao'),
                                versao=paciente_vps.get('versao', 1),
                                status='ativo'
                            )
                            if resultado.get('success'):
                                resultados["pacientes_baixados"] += 1
                                logger.info(f"Paciente {pid_normalizado} inserido (novo)")
                                paciente_vps_encontrado = True
                            else:
                                resultados["erros"].append(f"Erro ao inserir paciente {pid_normalizado}: {resultado.get('message')}")
                        except Exception as e:
                            logger.error(f"Erro ao inserir paciente {pid_normalizado}: {e}")
                            resultados["erros"].append(f"Erro ao inserir paciente {pid_normalizado}: {str(e)}")
                else:
                    # Não achou por ID, tenta match por nome (caso de ID gerado temporariamente)
                    # Extrai nome do ID gerado temporariamente (ex: "Amelita_26_61450d7e" -> "Amelita_26")
                    partes_nome = pid_normalizado.split('_')
                    if len(partes_nome) >= 2:
                        nome_base = '_'.join(partes_nome[:-1])  # Remove apenas a última parte (timestamp aleatório)
                        logger.info(f"Tentando match por nome base: {nome_base}")
                        
                        for p in pacientes_vps:
                            if p.get('id') is None or p['id'] == 'null':
                                nome_vps = extrair_nome_paciente(p)
                                if nome_vps and normalizar_id(nome_vps) == nome_base:
                                    paciente_vps = p
                                    logger.info(f"Achou paciente VPS por nome: {nome_vps}")
                                    break
                    
                    if paciente_vps:
                        nome_vps = extrair_nome_paciente(paciente_vps)
                        if nome_vps and nome_vps in pl_by_nome:
                            paciente_local = pl_by_nome[nome_vps]
                            id_local = paciente_local.get('id')
                            try:
                                db.atualizar_paciente(id_local, paciente_vps)
                                resultados["pacientes_atualizados"] += 1
                                logger.info(f"Paciente {nome_vps} atualizado usando ID local {id_local} (match por Nome base)")
                                paciente_vps_encontrado = True
                            except Exception as e:
                                logger.error(f"Erro ao atualizar paciente por nome base {nome_vps}: {e}")
                                resultados["erros"].append(f"Erro ao atualizar paciente {nome_vps}: {str(e)}")
                        else:
                            # Insere novo
                            try:
                                resultado = db.inserir_registro(
                                    pid_normalizado,
                                    paciente_vps,
                                    pc_id=paciente_vps.get('pc_id'),
                                    ultima_modificacao=paciente_vps.get('ultima_modificacao'),
                                    versao=paciente_vps.get('versao', 1),
                                    status='ativo'
                                )
                                if resultado.get('success'):
                                    resultados["pacientes_baixados"] += 1
                                    logger.info(f"Paciente {pid_normalizado} inserido (novo via nome base)")
                                    paciente_vps_encontrado = True
                                else:
                                    resultados["erros"].append(f"Erro ao inserir paciente {pid_normalizado}: {resultado.get('message')}")
                            except Exception as e:
                                logger.error(f"Erro ao inserir paciente {pid_normalizado}: {e}")
                                resultados["erros"].append(f"Erro ao inserir paciente {pid_normalizado}: {str(e)}")
                
                if not paciente_vps_encontrado:
                    resultados["erros"].append(f"Paciente {pid_normalizado} não encontrado no VPS")
            
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
            return jsonify({"success": False, "message": str(e), "traceback": traceback.format_exc()}), 500

    @bp.route("/dados/deletar", methods=["POST"])
    def vps_deletar_dados():
        """Deleta dados selecionados do VPS"""
        try:
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
            return jsonify({"success": False, "message": str(e), "traceback": traceback.format_exc()}), 500
