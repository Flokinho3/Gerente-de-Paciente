"""Endpoints de gerenciamento de divergências VPS"""
from flask import Blueprint, jsonify


def register_vps_divergencias(bp: Blueprint):
    """Registra endpoints de divergências VPS"""
    
    @bp.route("/divergencias/pendentes", methods=["GET"])
    def vps_divergencias_pendentes():
        """Retorna todas as divergências pendentes detectadas"""
        try:
            from gerente.divergencias_manager import get_divergencias_manager
            divergencias_mgr = get_divergencias_manager()
            
            divergencias = divergencias_mgr.obter_divergencias()
            return jsonify({
                "success": True,
                "divergencias": divergencias
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    @bp.route("/divergencias/marcar-visto", methods=["POST"])
    def vps_divergencias_marcar_visto():
        """Marca todas as divergências atuais como já visualizadas (para parar alertas)"""
        try:
            from gerente.divergencias_manager import get_divergencias_manager
            
            divergencias_mgr = get_divergencias_manager()
            divergencias_mgr.marcar_todos_como_vistos()
            
            return jsonify({
                "success": True,
                "message": "Divergências marcadas como visualizadas"
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    @bp.route("/divergencias/novas", methods=["GET"])
    def vps_divergencias_novas():
        """Verifica se há divergências novas (ainda não notificadas)"""
        try:
            from gerente.divergencias_manager import get_divergencias_manager
            
            divergencias_mgr = get_divergencias_manager()
            tem_novas = divergencias_mgr.tem_divergencias_novas()
            
            return jsonify({
                "success": True,
                "tem_novas": tem_novas
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    @bp.route("/divergencias/marcar-notificadas", methods=["POST"])
    def vps_divergencias_marcar_notificadas():
        """Marca todas as divergências atuais como já notificadas"""
        try:
            from gerente.divergencias_manager import get_divergencias_manager
            
            divergencias_mgr = get_divergencias_manager()
            divergencias_mgr.marcar_todos_como_vistos()
            
            return jsonify({
                "success": True,
                "message": "Divergências marcadas como notificadas"
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    @bp.route("/divergencias/aplicar", methods=["POST"])
    def vps_divergencias_aplicar():
        """Aplica uma divergência (baixa do VPS para local)"""
        try:
            from flask import request
            from ..db import db
            from gerente.divergencias_manager import get_divergencias_manager
            
            data = request.get_json()
            item_id = data.get('item_id')
            tipo = data.get('tipo')
            dados = data.get('dados')
            
            if not item_id or not tipo or not dados:
                return jsonify({"success": False, "message": "Dados incompletos"}), 400
            
            if tipo == 'paciente':
                resultado = db.inserir_registro(
                    item_id,
                    dados,
                    pc_id=dados.get('pc_id'),
                    ultima_modificacao=dados.get('ultima_modificacao'),
                    versao=dados.get('versao'),
                    status='ativo'
                )
            elif tipo == 'agendamento':
                resultado = db.criar_agendamento(
                    agendamento_id=item_id,
                    paciente_id=dados.get('paciente_id'),
                    data_consulta=dados.get('data_consulta'),
                    hora_consulta=dados.get('hora_consulta'),
                    tipo_consulta=dados.get('tipo_consulta'),
                    observacoes=dados.get('observacoes'),
                    status=dados.get('status', 'agendado')
                )
            else:
                return jsonify({"success": False, "message": "Tipo inválido"}), 400
            
            if resultado.get('success'):
                divergencias_mgr = get_divergencias_manager()
                divergencias_mgr.resolver_divergencia(item_id)
                
                return jsonify({
                    "success": True,
                    "message": f"{tipo.capitalize()} aplicado com sucesso!"
                })
            else:
                return jsonify({"success": False, "message": resultado.get('message')}), 500
                
        except Exception as e:
            import traceback
            return jsonify({"success": False, "message": str(e), "traceback": traceback.format_exc()}), 500

    @bp.route("/divergencias/ignorar", methods=["POST"])
    def vps_divergencias_ignorar():
        """Ignora temporariamente uma divergência (até próxima sincronização)"""
        try:
            from flask import request
            from gerente.divergencias_manager import get_divergencias_manager
            
            data = request.get_json()
            item_id = data.get('item_id')
            
            if not item_id:
                return jsonify({"success": False, "message": "ID não fornecido"}), 400
            
            divergencias_mgr = get_divergencias_manager()
            divergencias_mgr.ignorar_temporario(item_id)
            
            return jsonify({
                "success": True,
                "message": "Divergência ignorada até a próxima sincronização"
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    @bp.route("/divergencias/remover", methods=["POST"])
    def vps_divergencias_remover():
        """Remove permanentemente uma divergência (não será mais notificada)"""
        try:
            from flask import request
            from gerente.divergencias_manager import get_divergencias_manager
            
            data = request.get_json()
            item_id = data.get('item_id')
            
            if not item_id:
                return jsonify({"success": False, "message": "ID não fornecido"}), 400
            
            divergencias_mgr = get_divergencias_manager()
            divergencias_mgr.remover_permanente(item_id)
            
            return jsonify({
                "success": True,
                "message": "Divergência removida permanentemente"
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    @bp.route("/divergencias/atualizar", methods=["POST"])
    def vps_divergencias_atualizar():
        """Atualiza com dados do VPS (para itens atualizados)"""
        try:
            from flask import request
            from ..db import db
            from gerente.divergencias_manager import get_divergencias_manager
            from gerente.vps_client import get_vps_client
            
            data = request.get_json()
            item_id = data.get('item_id')
            tipo = data.get('tipo')
            dados_vps = data.get('dados_vps')
            acao = data.get('acao')
            
            if not item_id or not tipo or not acao:
                return jsonify({"success": False, "message": "Dados incompletos"}), 400
            
            divergencias_mgr = get_divergencias_manager()
            vps_client = get_vps_client()
            resultado = None
            
            if acao == 'baixar':
                if tipo == 'paciente':
                    resultado = db.atualizar_paciente(item_id, dados_vps)
                elif tipo == 'agendamento':
                    resultado = db.atualizar_agendamento(item_id, dados_vps)
                else:
                    return jsonify({"success": False, "message": "Tipo inválido"}), 400
                
                if resultado and resultado.get('success'):
                    divergencias_mgr.resolver_divergencia(item_id)
                    return jsonify({"success": True, "message": "Dados atualizados do VPS"})
                else:
                    msg = resultado.get('message') if resultado else "Erro desconhecido"
                    return jsonify({"success": False, "message": msg}), 500
                    
            elif acao == 'enviar':
                if tipo == 'paciente':
                    paciente = db.buscar_paciente(item_id)
                    if paciente and vps_client:
                        resultado = vps_client.sync_pacientes([paciente])
                elif tipo == 'agendamento':
                    agendamento = db.obter_agendamento(item_id)
                    if agendamento and vps_client:
                        resultado = vps_client.sync_agendamentos([agendamento])
                else:
                    return jsonify({"success": False, "message": "Tipo inválido"}), 400
                
                if resultado and resultado.get('success'):
                    divergencias_mgr.resolver_divergencia(item_id)
                    return jsonify({"success": True, "message": "Dados enviados para VPS"})
                else:
                    msg = resultado.get('message') if resultado else "Erro desconhecido"
                    return jsonify({"success": False, "message": msg}), 500
            else:
                return jsonify({"success": False, "message": "Ação inválida"}), 400
                
        except Exception as e:
            import traceback
            return jsonify({"success": False, "message": str(e), "traceback": traceback.format_exc()}), 500
