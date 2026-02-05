"""
API: Backup e restauração do banco.
"""
import io
import json
from datetime import datetime

from flask import Blueprint, jsonify, make_response, request, send_file

from .db import db

bp = Blueprint("api_backup", __name__, url_prefix="/api/backup")


@bp.route("/criar", methods=["GET"])
def criar_backup():
    try:
        return jsonify(db.criar_backup())
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao criar backup: {str(e)}"}), 500


@bp.route("/download", methods=["GET"])
def download_backup():
    try:
        resultado = db.criar_backup()
        buf = io.BytesIO(json.dumps(resultado["backup"], ensure_ascii=False, indent=2).encode("utf-8"))
        buf.seek(0)
        name = f"backup_pacientes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        return make_response(
            send_file(buf, mimetype="application/json", as_attachment=True, download_name=name)
        )
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao gerar arquivo de backup: {str(e)}"}), 500


@bp.route("/restaurar", methods=["POST"])
def restaurar_backup():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Dados do backup não fornecidos"}), 400
        backup = data.get("backup") if isinstance(data, dict) else data
        if not isinstance(backup, list):
            return jsonify({"success": False, "message": "Backup deve ser uma lista de registros"}), 400
        resultado = db.restaurar_backup(backup)
        if resultado["success"]:
            return jsonify(resultado)
        return jsonify(resultado), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao restaurar backup: {str(e)}"}), 500


@bp.route("/validar", methods=["POST"])
def validar_backup():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Backup não fornecido"}), 400
        backup = data.get("backup") if isinstance(data, dict) else data
        if not isinstance(backup, list):
            return jsonify({"success": False, "message": "Backup deve ser uma lista de pacientes"}), 400
        erros = []
        for idx, reg in enumerate(backup):
            if not isinstance(reg, dict):
                erros.append(f"Item {idx + 1} não é um objeto válido")
                continue
            id_ = reg.get("identificacao", {})
            av = reg.get("avaliacao", {})
            if not id_.get("nome_gestante"):
                erros.append(f"Item {idx + 1} não possui nome da gestante")
            if not isinstance(av, dict) or "consultas_pre_natal" not in av:
                erros.append(f"Item {idx + 1} com avaliação incompleta")
        if erros:
            return jsonify({"success": False, "message": "Backup inválido", "errors": erros}), 400
        return jsonify({"success": True, "message": "Backup válido", "total": len(backup)})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao validar backup: {str(e)}"}), 500


@bp.route("/limpar", methods=["DELETE"])
def limpar_banco_dados():
    try:
        return jsonify(db.limpar_todos_dados())
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao limpar banco de dados: {str(e)}"}), 500


@bp.route("/comparar", methods=["POST"])
def comparar_backup():
    """
    Compara backup com banco atual e retorna diferenças detalhadas.
    Mostra: novos, modificados, idênticos e removidos.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Dados do backup não fornecidos"}), 400
        backup = data.get("backup") if isinstance(data, dict) else data
        if not isinstance(backup, list):
            return jsonify({"success": False, "message": "Backup deve ser uma lista de registros"}), 400
        
        # Debug: imprimir estrutura do primeiro item
        if backup and len(backup) > 0:
            print(f"[DEBUG] Primeiro item do backup: {backup[0].keys() if isinstance(backup[0], dict) else 'Não é dict'}")
            print(f"[DEBUG] Total de registros no backup: {len(backup)}")
        
        resultado = db.comparar_backup(backup)
        
        # Debug: imprimir resultado
        if resultado.get("success") and resultado.get("comparison"):
            comp = resultado["comparison"]
            print(f"[DEBUG] Comparação - Novos: {len(comp.get('novos', []))}, Modificados: {len(comp.get('modificados', []))}, Idênticos: {len(comp.get('identicos', []))}, Removidos: {len(comp.get('removidos', []))}")
        
        return jsonify(resultado)
    except Exception as e:
        import traceback
        print(f"[DEBUG] Erro ao comparar: {traceback.format_exc()}")
        return jsonify({"success": False, "message": f"Erro ao comparar backup: {str(e)}"}), 500


@bp.route("/importar_com_acoes", methods=["POST"])
def importar_com_acoes():
    """
    Importa pacientes com ações individuais: confirmar, editar, ignorar.
    Itens marcados como 'ignorar' vão para tabela temporária (5 dias).
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Dados não fornecidos"}), 400
        
        # Estrutura esperada:
        # {
        #   "novos": [{"paciente": {...}, "acao": "confirmar|editar|ignorar", "motivo": "..."}, ...],
        #   "modificados": [{"paciente": {...}, "acao": "confirmar|editar|ignorar", "motivo": "..."}, ...],
        #   "origem_backup": "nome_arquivo.json"
        # }
        
        novos = data.get("novos", [])
        modificados = data.get("modificados", [])
        origem_backup = data.get("origem_backup", "importacao_manual")
        
        if not novos and not modificados:
            return jsonify({"success": False, "message": "Nenhum paciente selecionado para importação"}), 400
        
        resultados = {
            "adicionados": 0,
            "atualizados": 0,
            "ignorados": 0,
            "erros": [],
            "itens_ignorados": []
        }
        
        # Limpar itens ignorados expirados antes de começar
        db.limpar_itens_ignorados_expirados()
        
        # Processar novos pacientes
        for item in novos:
            try:
                paciente = item.get("paciente", {})
                acao = item.get("acao", "ignorar")  # Padrão: ignorar
                motivo = item.get("motivo", "")
                paciente_id = paciente.get("id") or db.gerar_id(
                    paciente.get("identificacao", {}).get("nome_gestante", "")
                )
                
                if acao == "ignorar":
                    # Adicionar à tabela de itens ignorados
                    resultado_ignorado = db.adicionar_item_ignorado(
                        paciente_id=paciente_id,
                        dados_backup=json.dumps(paciente),
                        origem_backup=origem_backup,
                        motivo=motivo or "Ignorado durante importação"
                    )
                    if resultado_ignorado["success"]:
                        resultados["ignorados"] += 1
                        resultados["itens_ignorados"].append({
                            "id": resultado_ignorado["id"],
                            "paciente_id": paciente_id,
                            "nome": paciente.get("identificacao", {}).get("nome_gestante", "")
                        })
                elif acao == "confirmar":
                    # Importar paciente
                    resultado = db.inserir_registro(
                        paciente_id,
                        paciente,
                        arquivo_origem=origem_backup,
                        data_salvamento=paciente.get("data_salvamento"),
                        pc_id=paciente.get("pc_id"),
                        ultima_modificacao=paciente.get("ultima_modificacao"),
                        versao=paciente.get("versao", 1),
                        status=paciente.get("status", "ativo")
                    )
                    if resultado["success"]:
                        resultados["adicionados"] += 1
                    else:
                        resultados["erros"].append(f"Erro ao adicionar {paciente_id}: {resultado.get('message')}")
                elif acao == "editar":
                    # Salvar em itens ignorados para edição posterior
                    resultado_ignorado = db.adicionar_item_ignorado(
                        paciente_id=paciente_id,
                        dados_backup=json.dumps(paciente),
                        origem_backup=origem_backup,
                        motivo=motivo or "Marcado para edição"
                    )
                    if resultado_ignorado["success"]:
                        resultados["ignorados"] += 1
                        resultados["itens_ignorados"].append({
                            "id": resultado_ignorado["id"],
                            "paciente_id": paciente_id,
                            "nome": paciente.get("identificacao", {}).get("nome_gestante", ""),
                            "para_edicao": True
                        })
            except Exception as e:
                resultados["erros"].append(f"Erro ao processar paciente: {str(e)}")
        
        # Processar pacientes modificados (mesma lógica)
        for item in modificados:
            try:
                paciente = item.get("paciente", {})
                acao = item.get("acao", "ignorar")
                motivo = item.get("motivo", "")
                paciente_id = paciente.get("id")
                
                if not paciente_id:
                    continue
                
                if acao == "ignorar":
                    resultado_ignorado = db.adicionar_item_ignorado(
                        paciente_id=paciente_id,
                        dados_backup=json.dumps(paciente),
                        origem_backup=origem_backup,
                        motivo=motivo or "Ignorado durante importação"
                    )
                    if resultado_ignorado["success"]:
                        resultados["ignorados"] += 1
                        resultados["itens_ignorados"].append({
                            "id": resultado_ignorado["id"],
                            "paciente_id": paciente_id,
                            "nome": paciente.get("identificacao", {}).get("nome_gestante", "")
                        })
                elif acao == "confirmar":
                    resultado = db.atualizar_paciente(paciente_id, paciente)
                    if resultado["success"]:
                        resultados["atualizados"] += 1
                    else:
                        resultados["erros"].append(f"Erro ao atualizar {paciente_id}: {resultado.get('message')}")
                elif acao == "editar":
                    resultado_ignorado = db.adicionar_item_ignorado(
                        paciente_id=paciente_id,
                        dados_backup=json.dumps(paciente),
                        origem_backup=origem_backup,
                        motivo=motivo or "Marcado para edição"
                    )
                    if resultado_ignorado["success"]:
                        resultados["ignorados"] += 1
                        resultados["itens_ignorados"].append({
                            "id": resultado_ignorado["id"],
                            "paciente_id": paciente_id,
                            "nome": paciente.get("identificacao", {}).get("nome_gestante", ""),
                            "para_edicao": True
                        })
            except Exception as e:
                resultados["erros"].append(f"Erro ao atualizar paciente: {str(e)}")
        
        return jsonify({
            "success": True,
            "message": f"Processamento concluído: {resultados['adicionados']} adicionados, {resultados['atualizados']} atualizados, {resultados['ignorados']} ignorados",
            "adicionados": resultados["adicionados"],
            "atualizados": resultados["atualizados"],
            "ignorados": resultados["ignorados"],
            "itens_ignorados": resultados["itens_ignorados"],
            "erros": resultados["erros"]
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao importar: {str(e)}"}), 500


@bp.route("/importar_selecionados", methods=["POST"])
def importar_selecionados():
    """
    Importa apenas os pacientes selecionados do backup (método legado).
    Permite importação seletiva em vez de substituir tudo.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Dados não fornecidos"}), 400
        
        novos = data.get("novos", [])
        modificados = data.get("modificados", [])
        substituir_todos = data.get("substituir_todos", False)
        
        if not novos and not modificados:
            return jsonify({"success": False, "message": "Nenhum paciente selecionado para importação"}), 400
        
        resultados = {
            "adicionados": 0,
            "atualizados": 0,
            "erros": []
        }
        
        # Se substituir_todos for True, limpar banco primeiro
        if substituir_todos:
            db.limpar_todos_dados()
        
        # Processar novos pacientes
        for paciente in novos:
            try:
                paciente_id = paciente.get("id") or db.gerar_id(
                    paciente.get("identificacao", {}).get("nome_gestante", "")
                )
                resultado = db.inserir_registro(
                    paciente_id,
                    paciente,
                    arquivo_origem=paciente.get("arquivo_origem", "importacao_seletiva"),
                    data_salvamento=paciente.get("data_salvamento"),
                    pc_id=paciente.get("pc_id"),
                    ultima_modificacao=paciente.get("ultima_modificacao"),
                    versao=paciente.get("versao", 1),
                    status=paciente.get("status", "ativo")
                )
                if resultado["success"]:
                    resultados["adicionados"] += 1
                else:
                    resultados["erros"].append(f"Erro ao adicionar {paciente_id}: {resultado.get('message')}")
            except Exception as e:
                resultados["erros"].append(f"Erro ao processar paciente: {str(e)}")
        
        # Processar pacientes modificados
        for paciente in modificados:
            try:
                paciente_id = paciente.get("id")
                if not paciente_id:
                    continue
                    
                # Atualizar paciente existente
                resultado = db.atualizar_paciente(paciente_id, paciente)
                if resultado["success"]:
                    resultados["atualizados"] += 1
                else:
                    resultados["erros"].append(f"Erro ao atualizar {paciente_id}: {resultado.get('message')}")
            except Exception as e:
                resultados["erros"].append(f"Erro ao atualizar paciente: {str(e)}")
        
        total = resultados["adicionados"] + resultados["atualizados"]
        return jsonify({
            "success": True,
            "message": f"Importação concluída: {total} pacientes processados",
            "adicionados": resultados["adicionados"],
            "atualizados": resultados["atualizados"],
            "erros": resultados["erros"]
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao importar selecionados: {str(e)}"}), 500


@bp.route("/executar_importacao", methods=["POST"])
def executar_importacao():
    """
    Executa a importação baseada nas ações selecionadas pelo usuário.
    Payload esperado:
    {
        "nome_arquivo": "backup.json",
        "acoes": {
            "novos": {"id1": {"acao": "confirmar", "motivo": ""}, ...},
            "modificados": {"id2": {"acao": "editar", "motivo": "ajuste"}, ...}
        }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Dados não fornecidos"}), 400
        
        acoes = data.get("acoes", {})
        nome_arquivo = data.get("nome_arquivo", "importacao_manual")
        
        novos_acoes = acoes.get("novos", {})
        modificados_acoes = acoes.get("modificados", {})
        
        # Verificar se há alguma ação diferente de "ignorar"
        tem_acao = False
        for tipo_acoes in [novos_acoes, modificados_acoes]:
            for item_id, acao_data in tipo_acoes.items():
                if isinstance(acao_data, dict) and acao_data.get("acao") != "ignorar":
                    tem_acao = True
                    break
                elif isinstance(acao_data, str) and acao_data != "ignorar":
                    tem_acao = True
                    break
        
        if not tem_acao:
            return jsonify({"success": False, "message": "Nenhuma ação selecionada. Escolha ao menos um paciente para confirmar ou editar."}), 400
        
        resultados = {
            "adicionados": 0,
            "atualizados": 0,
            "ignorados": 0,
            "itens_ignorados": [],
            "erros": []
        }
        
        # Limpar itens expirados antes de começar
        db.limpar_itens_ignorados_expirados()
        
        # Processar novos pacientes
        for item_id, acao_data in novos_acoes.items():
            try:
                # Extrair ação e motivo
                if isinstance(acao_data, dict):
                    acao = acao_data.get("acao", "ignorar")
                    motivo = acao_data.get("motivo", "")
                    paciente = acao_data.get("paciente", {})
                else:
                    # Formato legado (string)
                    acao = acao_data
                    motivo = ""
                    paciente = {}
                
                if acao == "ignorar":
                    # Adicionar à tabela de itens ignorados
                    if paciente:
                        resultado_ignorado = db.adicionar_item_ignorado(
                            paciente_id=item_id,
                            dados_backup=json.dumps(paciente),
                            origem_backup=nome_arquivo,
                            motivo=motivo or "Ignorado durante importação"
                        )
                        if resultado_ignorado["success"]:
                            resultados["ignorados"] += 1
                            resultados["itens_ignorados"].append({
                                "id": resultado_ignorado["id"],
                                "paciente_id": item_id,
                                "nome": paciente.get("identificacao", {}).get("nome_gestante", "")
                            })
                elif acao == "confirmar":
                    # Importar paciente
                    if paciente:
                        resultado = db.inserir_registro(
                            item_id,
                            paciente,
                            arquivo_origem=nome_arquivo,
                            data_salvamento=paciente.get("data_salvamento"),
                            pc_id=paciente.get("pc_id"),
                            ultima_modificacao=paciente.get("ultima_modificacao"),
                            versao=paciente.get("versao", 1),
                            status=paciente.get("status", "ativo")
                        )
                        if resultado["success"]:
                            resultados["adicionados"] += 1
                        else:
                            resultados["erros"].append(f"Erro ao adicionar {item_id}: {resultado.get('message')}")
                elif acao == "editar":
                    # Salvar em itens ignorados para edição posterior
                    if paciente:
                        resultado_ignorado = db.adicionar_item_ignorado(
                            paciente_id=item_id,
                            dados_backup=json.dumps(paciente),
                            origem_backup=nome_arquivo,
                            motivo=motivo or "Marcado para edição"
                        )
                        if resultado_ignorado["success"]:
                            resultados["ignorados"] += 1
                            resultados["itens_ignorados"].append({
                                "id": resultado_ignorado["id"],
                                "paciente_id": item_id,
                                "nome": paciente.get("identificacao", {}).get("nome_gestante", ""),
                                "para_edicao": True
                            })
            except Exception as e:
                resultados["erros"].append(f"Erro ao processar paciente {item_id}: {str(e)}")
        
        # Processar pacientes modificados
        for item_id, acao_data in modificados_acoes.items():
            try:
                # Extrair ação e motivo
                if isinstance(acao_data, dict):
                    acao = acao_data.get("acao", "ignorar")
                    motivo = acao_data.get("motivo", "")
                    paciente = acao_data.get("paciente", {})
                else:
                    # Formato legado (string)
                    acao = acao_data
                    motivo = ""
                    paciente = {}
                
                if acao == "ignorar":
                    if paciente:
                        resultado_ignorado = db.adicionar_item_ignorado(
                            paciente_id=item_id,
                            dados_backup=json.dumps(paciente),
                            origem_backup=nome_arquivo,
                            motivo=motivo or "Ignorado durante importação"
                        )
                        if resultado_ignorado["success"]:
                            resultados["ignorados"] += 1
                            resultados["itens_ignorados"].append({
                                "id": resultado_ignorado["id"],
                                "paciente_id": item_id,
                                "nome": paciente.get("identificacao", {}).get("nome_gestante", "")
                            })
                elif acao == "confirmar":
                    if paciente:
                        resultado = db.atualizar_paciente(item_id, paciente)
                        if resultado["success"]:
                            resultados["atualizados"] += 1
                        else:
                            resultados["erros"].append(f"Erro ao atualizar {item_id}: {resultado.get('message')}")
                elif acao == "editar":
                    if paciente:
                        resultado_ignorado = db.adicionar_item_ignorado(
                            paciente_id=item_id,
                            dados_backup=json.dumps(paciente),
                            origem_backup=nome_arquivo,
                            motivo=motivo or "Marcado para edição"
                        )
                        if resultado_ignorado["success"]:
                            resultados["ignorados"] += 1
                            resultados["itens_ignorados"].append({
                                "id": resultado_ignorado["id"],
                                "paciente_id": item_id,
                                "nome": paciente.get("identificacao", {}).get("nome_gestante", ""),
                                "para_edicao": True
                            })
            except Exception as e:
                resultados["erros"].append(f"Erro ao processar paciente {item_id}: {str(e)}")
        
        total_processados = resultados["adicionados"] + resultados["atualizados"] + resultados["ignorados"]
        
        return jsonify({
            "success": True,
            "message": f"Importação concluída: {resultados['adicionados']} adicionados, {resultados['atualizados']} atualizados, {resultados['ignorados']} ignorados",
            "processados": total_processados,
            "adicionados": resultados["adicionados"],
            "atualizados": resultados["atualizados"],
            "ignorados": resultados["ignorados"],
            "itens_ignorados": resultados["itens_ignorados"],
            "erros": resultados["erros"]
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao executar importação: {str(e)}"}), 500
