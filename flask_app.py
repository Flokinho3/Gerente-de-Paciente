"""
Aplicação Flask - Sistema de Gestão de Pacientes
Contém todas as rotas e lógica do Flask
"""
import json
import os
import io
import subprocess
import sys
import atexit
from flask import Flask, jsonify, render_template, request, send_file, make_response
from datetime import datetime
from dotenv import load_dotenv
from database import db

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Versão do sistema
VERSION = "1.0.2"
BUILD_DATE = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

app = Flask(__name__)

# Injetar versão em todos os templates
@app.context_processor
def inject_version():
    return dict(version=VERSION, build_date=BUILD_DATE)

@app.route('/')
def home():
    return render_template('Home.html')

@app.route('/novo_paciente')
def novo_paciente():
    return render_template('novo_paciente.html')

@app.route('/pacientes')
def pacientes():
    return render_template('pacientes.html')

@app.route('/exportar')
def exportar():
    return render_template('exportar.html')

@app.route('/bd')
def bd():
    return render_template('bd.html')

@app.route('/agendamentos')
def agendamentos():
    return render_template('agendamentos.html')

@app.route('/api/version', methods=['GET'])
def get_version():
    """Retorna a versão atual do sistema"""
    return jsonify({
        'success': True,
        'version': VERSION,
        'build_date': BUILD_DATE
    })

@app.route('/api/abrir_ajuda', methods=['GET'])
def abrir_ajuda():
    """Abre o arquivo de ajuda no Bloco de Notas do Windows"""
    try:
        caminho_ajuda = None
        
        # Detectar se está rodando como executável ou em desenvolvimento
        if getattr(sys, 'frozen', False):
            # Modo executável: procurar em vários locais possíveis
            # 1. No diretório temporário do PyInstaller (sys._MEIPASS)
            if hasattr(sys, '_MEIPASS'):
                caminho_temp = os.path.join(sys._MEIPASS, 'COMO_USAR.txt')
                if os.path.exists(caminho_temp):
                    caminho_ajuda = caminho_temp
            
            # 2. No diretório do executável
            if not caminho_ajuda:
                caminho_exe = os.path.join(os.path.dirname(sys.executable), 'COMO_USAR.txt')
                if os.path.exists(caminho_exe):
                    caminho_ajuda = caminho_exe
        else:
            # Modo desenvolvimento: usar o diretório do script
            caminho_ajuda = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'COMO_USAR.txt')
        
        # Verificar se o arquivo existe
        if not caminho_ajuda or not os.path.exists(caminho_ajuda):
            return jsonify({'success': False, 'message': 'Arquivo de ajuda não encontrado'}), 404

        # Abrir no Bloco de Notas do Windows
        subprocess.Popen(['notepad.exe', caminho_ajuda])
        
        return jsonify({'success': True, 'message': 'Arquivo de ajuda aberto no Bloco de Notas'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao abrir ajuda: {str(e)}'}), 500

@app.route('/api/salvar_paciente', methods=['POST'])
def salvar_paciente():
    """Salva os dados do paciente usando o banco de dados"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        if not data or 'identificacao' not in data or 'avaliacao' not in data:
            return jsonify({'success': False, 'message': 'Dados inválidos'}), 400
        
        nome = data['identificacao'].get('nome_gestante', '').strip()
        if not nome:
            return jsonify({'success': False, 'message': 'Nome da gestante é obrigatório'}), 400
        
        # Salvar usando o banco de dados
        resultado = db.adicionar_paciente(data)
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao salvar: {str(e)}'}), 500

@app.route('/api/pacientes', methods=['GET'])
def listar_pacientes():
    """Lista todos os pacientes ou filtra por parâmetros"""
    try:
        filtro = {}
        
        # Filtros opcionais via query parameters
        nome = request.args.get('nome')
        unidade = request.args.get('unidade_saude')
        
        if nome:
            filtro['nome'] = nome
        if unidade:
            filtro['unidade_saude'] = unidade
        
        pacientes = db.buscar_pacientes(filtro if filtro else None)
        
        return jsonify({
            'success': True,
            'total': len(pacientes),
            'pacientes': pacientes
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Erro ao buscar pacientes: {error_details}")
        return jsonify({
            'success': False, 
            'message': f'Erro ao buscar pacientes: {str(e)}',
            'error': str(e)
        }), 500

@app.route('/api/atualizar_paciente/<paciente_id>', methods=['PUT'])
def atualizar_paciente(paciente_id):
    """Atualiza os dados de um paciente existente"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        if not data or 'identificacao' not in data or 'avaliacao' not in data:
            return jsonify({'success': False, 'message': 'Dados inválidos'}), 400
        
        # Atualizar usando o banco de dados
        resultado = db.atualizar_paciente(paciente_id, data)
        
        if resultado['success']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 404
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao atualizar: {str(e)}'}), 500

@app.route('/api/deletar_paciente/<paciente_id>', methods=['DELETE'])
def deletar_paciente(paciente_id):
    """Deleta um paciente do banco de dados"""
    try:
        resultado = db.deletar_paciente(paciente_id)
        
        if resultado['success']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao deletar: {str(e)}'}), 500

# Rotas de API para Agendamentos
@app.route('/api/agendamentos', methods=['GET'])
def listar_agendamentos():
    """Lista agendamentos com filtros opcionais"""
    try:
        paciente_id = request.args.get('paciente_id')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        status = request.args.get('status')
        
        agendamentos = db.listar_agendamentos(
            paciente_id=paciente_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            status=status
        )
        
        return jsonify({
            'success': True,
            'agendamentos': agendamentos
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar agendamentos: {str(e)}'
        }), 500

@app.route('/api/agendamentos', methods=['POST'])
def criar_agendamento():
    """Cria um novo agendamento"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        paciente_id = data.get('paciente_id')
        data_consulta = data.get('data_consulta')
        hora_consulta = data.get('hora_consulta')
        
        if not paciente_id or not data_consulta or not hora_consulta:
            return jsonify({
                'success': False,
                'message': 'Dados obrigatórios faltando: paciente_id, data_consulta, hora_consulta'
            }), 400
        
        # Gerar ID único
        import uuid
        agendamento_id = str(uuid.uuid4())
        
        tipo_consulta = data.get('tipo_consulta')
        observacoes = data.get('observacoes')
        status = data.get('status', 'agendado')
        
        resultado = db.criar_agendamento(
            agendamento_id=agendamento_id,
            paciente_id=paciente_id,
            data_consulta=data_consulta,
            hora_consulta=hora_consulta,
            tipo_consulta=tipo_consulta,
            observacoes=observacoes,
            status=status
        )
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao criar agendamento: {str(e)}'
        }), 500

@app.route('/api/agendamentos/<agendamento_id>', methods=['GET'])
def obter_agendamento(agendamento_id):
    """Obtém um agendamento específico"""
    try:
        agendamento = db.obter_agendamento(agendamento_id)
        if agendamento:
            return jsonify({
                'success': True,
                'agendamento': agendamento
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Agendamento não encontrado'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter agendamento: {str(e)}'
        }), 500

@app.route('/api/agendamentos/<agendamento_id>', methods=['PUT'])
def atualizar_agendamento(agendamento_id):
    """Atualiza um agendamento existente"""
    try:
        data = request.get_json()
        
        resultado = db.atualizar_agendamento(
            agendamento_id=agendamento_id,
            data_consulta=data.get('data_consulta'),
            hora_consulta=data.get('hora_consulta'),
            tipo_consulta=data.get('tipo_consulta'),
            observacoes=data.get('observacoes'),
            status=data.get('status')
        )
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar agendamento: {str(e)}'
        }), 500

@app.route('/api/agendamentos/<agendamento_id>', methods=['DELETE'])
def deletar_agendamento(agendamento_id):
    """Deleta um agendamento"""
    try:
        resultado = db.excluir_agendamento(agendamento_id)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao deletar agendamento: {str(e)}'
        }), 500

@app.route('/api/sync/discover', methods=['GET'])
def discover_servers():
    """Descobre outros servidores na rede local"""
    try:
        import socket
        import threading
        import time
        
        # Obter IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
        except:
            local_ip = '127.0.0.1'
        finally:
            s.close()
        
        # Obter porta atual
        port = int(os.getenv('PORT', 5000))
        
        # Descobrir outros servidores na rede
        discovered_servers = []
        ip_parts = local_ip.split('.')
        base_ip = '.'.join(ip_parts[:-1])
        
        def check_server(ip):
            try:
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.settimeout(0.5)
                result = test_socket.connect_ex((ip, port))
                test_socket.close()
                
                if result == 0:
                    # Tentar fazer requisição HTTP
                    import urllib.request
                    try:
                        url = f'http://{ip}:{port}/api/version'
                        req = urllib.request.Request(url, timeout=1)
                        response = urllib.request.urlopen(req)
                        if response.status == 200:
                            discovered_servers.append({
                                'ip': ip,
                                'port': port,
                                'hostname': socket.gethostbyaddr(ip)[0] if ip != local_ip else socket.gethostname()
                            })
                    except:
                        pass
            except:
                pass
        
        # Verificar IPs na mesma rede (último octeto de 1 a 254)
        threads = []
        for i in range(1, 255):
            ip = f'{base_ip}.{i}'
            if ip != local_ip:  # Não verificar o próprio IP
                thread = threading.Thread(target=check_server, args=(ip,))
                thread.daemon = True
                thread.start()
                threads.append(thread)
        
        # Aguardar um pouco para as threads terminarem
        time.sleep(2)
        
        return jsonify({
            'success': True,
            'local_ip': local_ip,
            'port': port,
            'servers': discovered_servers
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao descobrir servidores: {str(e)}'
        }), 500

@app.route('/api/sync/data', methods=['GET'])
def get_sync_data():
    """Retorna dados para sincronização (pacientes e agendamentos)"""
    try:
        pacientes = db.buscar_pacientes()
        agendamentos = db.listar_agendamentos()
        
        return jsonify({
            'success': True,
            'pacientes': pacientes,
            'agendamentos': agendamentos,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter dados para sincronização: {str(e)}'
        }), 500

@app.route('/api/sync/merge', methods=['POST'])
def merge_sync_data():
    """Recebe dados de sincronização e faz merge inteligente (adiciona, atualiza e detecta remoções)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        pacientes_remotos = data.get('pacientes', [])
        agendamentos_remotos = data.get('agendamentos', [])
        
        # Comparar bancos para detectar pacientes removidos no remoto
        comparacao = db.comparar_com_banco_remoto(pacientes_remotos)
        
        # Obter pacientes locais e seus IDs
        pacientes_locais = db.buscar_pacientes()
        pacientes_locais_ids = {p['id'] for p in pacientes_locais}
        
        # Obter agendamentos locais
        agendamentos_locais = db.listar_agendamentos()
        agendamentos_locais_ids = {a['id'] for a in agendamentos_locais}
        
        # Estatísticas
        pacientes_adicionados = 0
        pacientes_atualizados = 0
        agendamentos_adicionados = 0
        agendamentos_atualizados = 0
        
        # Sincronizar pacientes (adicionar novos e atualizar existentes)
        for paciente_remoto in pacientes_remotos:
            paciente_id = paciente_remoto['id']
            
            if paciente_id in pacientes_locais_ids:
                # Paciente já existe localmente - atualizar se dados remotos forem mais recentes
                paciente_local = next((p for p in pacientes_locais if p['id'] == paciente_id), None)
                if paciente_local:
                    data_local = paciente_local.get('data_salvamento', '')
                    data_remota = paciente_remoto.get('data_salvamento', '')
                    
                    # Se dados remotos são mais recentes ou iguais, atualizar
                    if data_remota >= data_local:
                        try:
                            db.atualizar_paciente(paciente_id, paciente_remoto)
                            pacientes_atualizados += 1
                        except:
                            pass
            else:
                # Paciente novo - adicionar
                try:
                    # Usar inserir_registro diretamente para manter o ID original
                    db.inserir_registro(
                        paciente_id,
                        paciente_remoto,
                        arquivo_origem='sync',
                        data_salvamento=paciente_remoto.get('data_salvamento')
                    )
                    pacientes_adicionados += 1
                except Exception as e:
                    # Se falhar, tentar adicionar normalmente
                    try:
                        db.adicionar_paciente(paciente_remoto)
                        pacientes_adicionados += 1
                    except:
                        pass
        
        # Sincronizar agendamentos (só adicionar/atualizar, nunca remover)
        for agendamento_remoto in agendamentos_remotos:
            agendamento_id = agendamento_remoto['id']
            
            if agendamento_id in agendamentos_locais_ids:
                # Agendamento já existe - atualizar se dados remotos forem mais recentes
                agendamento_local = next((a for a in agendamentos_locais if a['id'] == agendamento_id), None)
                if agendamento_local:
                    data_atualizacao_local = agendamento_local.get('data_atualizacao', '')
                    data_atualizacao_remota = agendamento_remoto.get('data_atualizacao', '')
                    
                    if data_atualizacao_remota >= data_atualizacao_local:
                        try:
                            db.atualizar_agendamento(
                                agendamento_id,
                                agendamento_remoto['paciente_id'],
                                agendamento_remoto['data_consulta'],
                                agendamento_remoto['hora_consulta'],
                                agendamento_remoto.get('tipo_consulta'),
                                agendamento_remoto.get('status', 'agendado'),
                                agendamento_remoto.get('observacoes')
                            )
                            agendamentos_atualizados += 1
                        except:
                            pass
            else:
                # Agendamento novo - adicionar
                try:
                    db.criar_agendamento(
                        agendamento_id,
                        agendamento_remoto['paciente_id'],
                        agendamento_remoto['data_consulta'],
                        agendamento_remoto['hora_consulta'],
                        agendamento_remoto.get('tipo_consulta'),
                        agendamento_remoto.get('status', 'agendado'),
                        agendamento_remoto.get('observacoes'),
                        agendamento_remoto.get('data_criacao'),
                        agendamento_remoto.get('data_atualizacao')
                    )
                    agendamentos_adicionados += 1
                except Exception as e:
                    pass
        
        # Preparar informações dos pacientes removidos no servidor remoto
        # (para o cliente decidir se quer remover também localmente)
        pacientes_removidos_info = [
            {
                'id': p['id'],
                'nome_gestante': p.get('identificacao', {}).get('nome_gestante') or p.get('nome_gestante', 'Sem nome'),
                'unidade_saude': p.get('identificacao', {}).get('unidade_saude') or p.get('unidade_saude', ''),
                'data_salvamento': p.get('data_salvamento', '')
            }
            for p in comparacao['pacientes_removidos_no_remoto']
        ]
        
        return jsonify({
            'success': True,
            'message': 'Sincronização concluída',
            'stats': {
                'pacientes_adicionados': pacientes_adicionados,
                'pacientes_atualizados': pacientes_atualizados,
                'agendamentos_adicionados': agendamentos_adicionados,
                'agendamentos_atualizados': agendamentos_atualizados
            },
            'pacientes_removidos': pacientes_removidos_info  # Para o cliente decidir se quer remover também
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': f'Erro ao sincronizar: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/sync/remover_pacientes', methods=['POST'])
def remover_pacientes_confirmados():
    """Remove pacientes após confirmação do usuário"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        paciente_ids = data.get('paciente_ids', [])
        if not paciente_ids:
            return jsonify({'success': False, 'message': 'Nenhum ID fornecido'}), 400
        
        resultado = db.remover_pacientes(paciente_ids)
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao remover pacientes: {str(e)}'
        }), 500

@app.route('/api/backup/criar', methods=['GET'])
def criar_backup():
    """Cria um backup completo do banco de dados"""
    try:
        resultado = db.criar_backup()
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao criar backup: {str(e)}'}), 500

@app.route('/api/backup/download', methods=['GET'])
def download_backup():
    """Permite baixar o último backup como arquivo JSON"""
    try:
        resultado = db.criar_backup()
        buffer = io.BytesIO(json.dumps(resultado['backup'], ensure_ascii=False, indent=2).encode('utf-8'))
        buffer.seek(0)
        filename = f"backup_pacientes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        response = make_response(send_file(
            buffer,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        ))
        return response
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao gerar arquivo de backup: {str(e)}'}), 500

@app.route('/api/backup/restaurar', methods=['POST'])
def restaurar_backup():
    """Restaura o banco de dados a partir de um backup"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Dados do backup não fornecidos'}), 400

        backup = data.get('backup') if isinstance(data, dict) else data
        if not isinstance(backup, list):
            return jsonify({'success': False, 'message': 'Backup deve ser uma lista de registros'}), 400

        resultado = db.restaurar_backup(backup)
        
        if resultado['success']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao restaurar backup: {str(e)}'}), 500

@app.route('/api/backup/validar', methods=['POST'])
def validar_backup():
    """Valida a estrutura do backup antes de restaurar"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Backup não fornecido'}), 400
        backup = data.get('backup') if isinstance(data, dict) else data
        if not isinstance(backup, list):
            return jsonify({'success': False, 'message': 'Backup deve ser uma lista de pacientes'}), 400
        erros = []
        for idx, registro in enumerate(backup):
            if not isinstance(registro, dict):
                erros.append(f'Item {idx + 1} não é um objeto válido')
                continue
            identificacao = registro.get('identificacao', {})
            avaliacao = registro.get('avaliacao', {})
            if not identificacao.get('nome_gestante'):
                erros.append(f'Item {idx + 1} não possui nome da gestante')
            if not isinstance(avaliacao, dict) or 'consultas_pre_natal' not in avaliacao:
                erros.append(f'Item {idx + 1} com avaliação incompleta')
        if erros:
            return jsonify({'success': False, 'message': 'Backup inválido', 'errors': erros}), 400
        return jsonify({'success': True, 'message': 'Backup válido', 'total': len(backup)})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao validar backup: {str(e)}'}), 500

@app.route('/api/backup/limpar', methods=['DELETE'])
def limpar_banco_dados():
    """Remove todos os dados do banco de dados"""
    try:
        resultado = db.limpar_todos_dados()
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao limpar banco de dados: {str(e)}'}), 500

@app.route('/api/indicadores')
def indicadores():
    """Calcula os indicadores agregados dos pacientes usando o banco de dados"""
    try:
        unidade_saude = request.args.get('unidade_saude')
        stats = db.obter_estatisticas(unidade_saude=unidade_saude)
        return jsonify({
            'total': stats['total_pacientes'],
            'inicio_pre_natal_antes_12s': stats['inicio_pre_natal_antes_12s'],
            'consultas_pre_natal': stats['consultas_pre_natal'],
            'vacinas_completas': stats['vacinas_completas'],
            'plano_parto': stats['plano_parto'],
            'participou_grupos': stats['participou_grupos']
        })
    except Exception as e:
        return jsonify({
            'total': 0,
            'inicio_pre_natal_antes_12s': {'sim': 0, 'nao': 0},
            'consultas_pre_natal': {'ate_6': 0, 'mais_6': 0},
            'vacinas_completas': {'completa': 0, 'incompleta': 0, 'nao_avaliado': 0},
            'plano_parto': {'sim': 0, 'nao': 0},
            'participou_grupos': {'sim': 0, 'nao': 0}
        }), 500

@app.route('/api/unidades_saude')
def listar_unidades_saude():
    """Lista todas as unidades de saúde únicas"""
    try:
        unidades = db.obter_unidades_saude_unicas()
        return jsonify({
            'success': True,
            'unidades': unidades
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar unidades: {str(e)}',
            'unidades': []
        }), 500

@app.route('/api/indicadores/temporais/<filtro>', methods=['GET'])
def indicadores_temporais(filtro):
    """Retorna estatísticas temporais agrupadas por data para um indicador específico"""
    try:
        # Validar filtro
        filtros_validos = ['inicio_pre_natal_antes_12s', 'consultas_pre_natal', 
                          'vacinas_completas', 'plano_parto', 'participou_grupos']
        if filtro not in filtros_validos:
            return jsonify({'error': 'Filtro inválido'}), 400
        
        stats_temporais = db.obter_estatisticas_temporais(filtro)
        return jsonify(stats_temporais)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/exportar/<formato>', methods=['GET'])
def exportar_pacientes(formato):
    """Exporta os dados dos pacientes no formato especificado"""
    try:
        # Aplicar filtro por unidade de saúde se fornecido
        filtro = {}
        unidade_saude = request.args.get('unidade_saude')
        if unidade_saude:
            filtro['unidade_saude'] = unidade_saude
            pacientes = db.buscar_pacientes(filtro)
        else:
            pacientes = db.obter_todos_pacientes()
        
        filtros = {
            'inicio_pre_natal': request.args.get('inicio_pre_natal'),
            'plano_parto': request.args.get('plano_parto'),
            'participou_grupos': request.args.get('participou_grupos'),
            'vacinas': request.args.get('vacinas')
        }
        pacientes_filtrados = aplicar_filtros_exportacao(pacientes, filtros)
        colunas_personalizadas = request.args.getlist('colunas')
        colunas_personalizadas = colunas_personalizadas if colunas_personalizadas else None

        if formato == 'excel':
            return exportar_excel(pacientes_filtrados, colunas_personalizadas)
        elif formato == 'word':
            return exportar_word(pacientes_filtrados, colunas_personalizadas)
        elif formato == 'txt':
            return exportar_txt(pacientes_filtrados, colunas_personalizadas)
        else:
            return jsonify({'success': False, 'message': 'Formato não suportado'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao exportar: {str(e)}'}), 500

def exportar_excel(pacientes, colunas_personalizadas=None):
    """Exporta dados para Excel (.xlsx)"""
    try:
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment
        except ImportError:
            return jsonify({
                'success': False,
                'message': 'Biblioteca openpyxl não encontrada. Instale com: pip install openpyxl'
            }), 500

        wb = Workbook()
        ws = wb.active
        ws.title = "Pacientes"

        colunas = obter_colunas_config(colunas_personalizadas)
        headers = [coluna['label'] for coluna in colunas]

        header_fill = PatternFill(start_color="667eea", end_color="764ba2", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=12)
        header_alignment = Alignment(horizontal="center", vertical="center")

        for col_idx, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment

        for row_idx, paciente in enumerate(pacientes, start=2):
            for col_idx, coluna in enumerate(colunas, start=1):
                ws.cell(row=row_idx, column=col_idx, value=obter_valor_coluna(paciente, coluna))

        for col_idx in range(1, len(headers) + 1):
            ws.column_dimensions[ws.cell(row=1, column=col_idx).column_letter].width = 22

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        filename = f"pacientes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response = make_response(send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        ))
        return response

    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao exportar Excel: {str(e)}'}), 500

def exportar_word(pacientes, colunas_personalizadas=None):
    """Exporta dados para Word (.docx)"""
    try:
        try:
            from docx import Document
            from docx.enum.text import WD_ALIGN_PARAGRAPH
        except ImportError:
            return jsonify({
                'success': False,
                'message': 'Biblioteca python-docx não encontrada. Instale com: pip install python-docx'
            }), 500

        doc = Document()
        colunas = obter_colunas_config(colunas_personalizadas)

        title = doc.add_heading('Relatório de Pacientes', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_paragraph(f'Total de pacientes: {len(pacientes)}')
        doc.add_paragraph(f'Data de exportação: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
        doc.add_paragraph('')

        for paciente in pacientes:
            ident = paciente.get('identificacao', {})
            nome = ident.get('nome_gestante', 'Nome não informado')
            doc.add_heading(nome, level=2)

            table = doc.add_table(rows=1, cols=2)
            table.style = 'Table Grid'
            header_cells = table.rows[0].cells
            header_cells[0].text = 'Campo'
            header_cells[1].text = 'Valor'

            for coluna in colunas:
                row_cells = table.add_row().cells
                row_cells[0].text = coluna['label']
                row_cells[1].text = str(obter_valor_coluna(paciente, coluna))

            doc.add_paragraph('')

        output = io.BytesIO()
        doc.save(output)
        output.seek(0)

        filename = f"pacientes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        response = make_response(send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=filename
        ))
        return response

    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao exportar Word: {str(e)}'}), 500

def exportar_txt(pacientes, colunas_personalizadas=None):
    """Exporta dados para arquivo de texto (.txt)"""
    try:
        output = io.StringIO()
        colunas = obter_colunas_config(colunas_personalizadas)

        output.write("=" * 80 + "\n")
        output.write("RELATÓRIO DE PACIENTES\n")
        output.write("=" * 80 + "\n")
        output.write(f"Total de pacientes: {len(pacientes)}\n")
        output.write(f"Data de exportação: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        output.write("=" * 80 + "\n\n")

        for idx, paciente in enumerate(pacientes, start=1):
            output.write(f"\n{'=' * 80}\n")
            output.write(f"PACIENTE {idx}\n")
            output.write(f"{'=' * 80}\n\n")

            for coluna in colunas:
                output.write(f"  {coluna['label']}: {obter_valor_coluna(paciente, coluna)}\n")
            output.write("\n")

        content = output.getvalue()
        output.close()
        output_bytes = io.BytesIO(content.encode('utf-8'))

        filename = f"pacientes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        response = make_response(send_file(
            output_bytes,
            mimetype='text/plain; charset=utf-8',
            as_attachment=True,
            download_name=filename
        ))
        return response

    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao exportar TXT: {str(e)}'}), 500

def aplicar_filtros_exportacao(pacientes, filtros):
    """Aplica os filtros selecionados antes da exportação"""
    if not any(filtros.values()):
        return pacientes

    resultados = []
    for paciente in pacientes:
        avaliacao = paciente.get('avaliacao', {})

        if filtros.get('inicio_pre_natal') and not avaliacao.get('inicio_pre_natal_antes_12s'):
            continue
        if filtros.get('plano_parto') and not avaliacao.get('plano_parto'):
            continue
        if filtros.get('participou_grupos') and not avaliacao.get('participou_grupos'):
            continue

        if filtros.get('vacinas'):
            status_vacina = (avaliacao.get('vacinas_completas', '') or '').lower()
            if not verificar_status_vacinas(status_vacina, filtros['vacinas']):
                continue

        resultados.append(paciente)

    return resultados

def verificar_status_vacinas(status, filtro):
    if filtro == 'completa':
        return 'complet' in status and 'incomplet' not in status
    if filtro == 'incompleta':
        return 'incomplet' in status
    if filtro == 'nao_avaliado':
        return status == '' or 'nao' in status or 'não' in status
    return True

def formatar_boolean(valor):
    """Formata valores booleanos para exibição"""
    if valor is True:
        return 'Sim'
    elif valor is False:
        return 'Não'
    return 'Não informado'

def formatar_vacinas(valor):
    if valor:
        return valor
    return 'Não avaliado'

COLUNAS_CONFIG = [
    {'key': 'identificacao.nome_gestante', 'label': 'Nome da Gestante'},
    {'key': 'identificacao.unidade_saude', 'label': 'Unidade de Saúde'},
    {'key': 'data_salvamento', 'label': 'Data de Cadastro'},
    {
        'key': 'avaliacao.inicio_pre_natal_antes_12s',
        'label': 'Início pré-natal antes de 12 semanas',
        'formatter': formatar_boolean
    },
    {'key': 'avaliacao.consultas_pre_natal', 'label': 'Consultas de pré-natal'},
    {
        'key': 'avaliacao.vacinas_completas',
        'label': 'Vacinas completas',
        'formatter': formatar_vacinas
    },
    {
        'key': 'avaliacao.plano_parto',
        'label': 'Plano de parto',
        'formatter': formatar_boolean
    },
    {
        'key': 'avaliacao.participou_grupos',
        'label': 'Participou de grupos',
        'formatter': formatar_boolean
    },
    {
        'key': 'avaliacao.avaliacao_odontologica',
        'label': 'Avaliação odontológica',
        'formatter': formatar_boolean
    },
    {
        'key': 'avaliacao.estratificacao',
        'label': 'Estratificação',
        'formatter': formatar_boolean
    },
    {
        'key': 'avaliacao.cartao_pre_natal_completo',
        'label': 'Cartão pré-natal completo',
        'formatter': formatar_boolean
    }
]

def obter_colunas_config(colunas_personalizadas):
    if colunas_personalizadas:
        selecionadas = [
            coluna for coluna in COLUNAS_CONFIG if coluna['key'] in colunas_personalizadas
        ]
        if selecionadas:
            return selecionadas
    return COLUNAS_CONFIG

def obter_valor_coluna(paciente, coluna):
    valor = paciente
    for parte in coluna['key'].split('.'):
        if isinstance(valor, dict):
            valor = valor.get(parte, '')
        else:
            valor = ''
    formatter = coluna.get('formatter')
    if callable(formatter):
        return formatter(valor)
    if valor is None:
        return ''
    return valor

# Variável global para armazenar o servidor Flask
_flask_server = None

def run_flask(debug=False, use_reloader=False, silent=False):
    """Inicia o servidor Flask"""
    global _flask_server
    
    # Obter configurações do .env ou usar padrões
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    # Se debug não foi passado explicitamente, verificar .env
    if debug is False:
        debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    if silent:
        # Modo silencioso: desabilitar logging do Werkzeug
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
    
    # Se não usar reloader, usar make_server para permitir shutdown
    if not use_reloader:
        try:
            from werkzeug.serving import make_server
            _flask_server = make_server(host, port, app)
            print(f"Servidor Flask iniciado em http://{host}:{port}")
            _flask_server.serve_forever()
        except KeyboardInterrupt:
            print("\nEncerrando servidor Flask...")
            if _flask_server:
                _flask_server.shutdown()
            print("Servidor Flask encerrado")
    else:
        # Modo desenvolvimento com reloader
        app.run(host=host, port=port, debug=debug, use_reloader=use_reloader)

def cleanup_flask():
    """Limpeza ao encerrar aplicação"""
    global _flask_server
    if _flask_server:
        try:
            print("Encerrando servidor Flask...")
            _flask_server.shutdown()
            _flask_server = None
            print("Servidor Flask encerrado")
        except:
            pass

# Registrar cleanup
atexit.register(cleanup_flask)
