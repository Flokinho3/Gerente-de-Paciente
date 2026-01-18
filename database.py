"""
Módulo de gerenciamento do banco de dados de pacientes
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class Database:
    """Classe para gerenciar o banco de dados de pacientes"""
    
    def __init__(self, db_file: str = 'database.json'):
        """
        Inicializa o banco de dados
        
        Args:
            db_file: Caminho do arquivo JSON do banco de dados
        """
        self.db_file = db_file
        self.pacientes_dir = os.path.join(
            os.path.dirname(__file__), 
            'static', 
            'Home', 
            'dados', 
            'Pacientes'
        )
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Garante que o arquivo do banco de dados existe"""
        if not os.path.exists(self.db_file):
            self._create_empty_db()
    
    def _create_empty_db(self):
        """Cria um banco de dados vazio"""
        empty_db = {
            'pacientes': [],
            'ultima_atualizacao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_pacientes': 0
        }
        self._save_db(empty_db)
    
    def _load_db(self) -> Dict:
        """Carrega o banco de dados do arquivo JSON"""
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._create_empty_db()
            return self._load_db()
    
    def _save_db(self, data: Dict):
        """Salva o banco de dados no arquivo JSON"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def adicionar_paciente(self, paciente_data: Dict) -> Dict:
        """
        Adiciona um novo paciente ao banco de dados
        
        Args:
            paciente_data: Dicionário com os dados do paciente
            
        Returns:
            Dicionário com o resultado da operação
        """
        db = self._load_db()
        
        # Criar ID único
        nome = paciente_data.get('identificacao', {}).get('nome_gestante', '')
        now = datetime.now()
        data_salvamento = now.strftime('%Y-%m-%d %H:%M:%S')
        
        # Verificar se já existe paciente com mesmo nome e data (evitar duplicatas)
        paciente_id = f"{nome}_{data_salvamento}".replace(' ', '_').replace(':', '').replace('-', '')
        
        # Adicionar dados ao paciente
        paciente_completo = {
            'id': paciente_id,
            'data_salvamento': data_salvamento,
            'identificacao': paciente_data.get('identificacao', {}),
            'avaliacao': paciente_data.get('avaliacao', {})
        }
        
        db['pacientes'].append(paciente_completo)
        db['total_pacientes'] = len(db['pacientes'])
        db['ultima_atualizacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self._save_db(db)
        
        # Também salvar arquivo individual na pasta (manter compatibilidade)
        nome_formatado = nome.replace(' ', '_')
        filename = f"{nome_formatado}_{now.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.pacientes_dir, filename)
        os.makedirs(self.pacientes_dir, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(paciente_completo, f, ensure_ascii=False, indent=4)
        
        return {
            'success': True,
            'message': 'Paciente adicionado com sucesso',
            'id': paciente_id,
            'filename': filename
        }
    
    def buscar_paciente(self, paciente_id: str) -> Optional[Dict]:
        """
        Busca um paciente pelo ID
        
        Args:
            paciente_id: ID do paciente
            
        Returns:
            Dados do paciente ou None se não encontrado
        """
        db = self._load_db()
        for paciente in db.get('pacientes', []):
            if paciente.get('id') == paciente_id:
                return paciente
        return None
    
    def atualizar_paciente(self, paciente_id: str, paciente_data: Dict) -> Dict:
        """
        Atualiza os dados de um paciente existente
        
        Args:
            paciente_id: ID do paciente
            paciente_data: Dicionário com os novos dados do paciente
            
        Returns:
            Dicionário com o resultado da operação
        """
        db = self._load_db()
        
        # Buscar paciente existente
        paciente_index = None
        for i, paciente in enumerate(db.get('pacientes', [])):
            if paciente.get('id') == paciente_id:
                paciente_index = i
                break
        
        if paciente_index is None:
            return {
                'success': False,
                'message': 'Paciente não encontrado'
            }
        
        # Atualizar dados
        now = datetime.now()
        paciente_atualizado = {
            'id': paciente_id,
            'data_salvamento': now.strftime('%Y-%m-%d %H:%M:%S'),
            'identificacao': paciente_data.get('identificacao', {}),
            'avaliacao': paciente_data.get('avaliacao', {})
        }
        
        # Manter arquivo_origem se existir
        paciente_antigo = db['pacientes'][paciente_index]
        if 'arquivo_origem' in paciente_antigo:
            paciente_atualizado['arquivo_origem'] = paciente_antigo['arquivo_origem']
        
        # Atualizar no banco
        db['pacientes'][paciente_index] = paciente_atualizado
        db['ultima_atualizacao'] = now.strftime('%Y-%m-%d %H:%M:%S')
        self._save_db(db)
        
        # Atualizar arquivo individual se existir
        if 'arquivo_origem' in paciente_atualizado:
            arquivo_origem = paciente_atualizado['arquivo_origem']
            filepath = os.path.join(self.pacientes_dir, arquivo_origem)
            if os.path.exists(filepath):
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(paciente_atualizado, f, ensure_ascii=False, indent=4)
        
        return {
            'success': True,
            'message': 'Paciente atualizado com sucesso',
            'id': paciente_id
        }
    
    def buscar_pacientes(self, filtro: Optional[Dict] = None) -> List[Dict]:
        """
        Busca pacientes com filtros opcionais
        
        Args:
            filtro: Dicionário com filtros (ex: {'nome': 'Ana'})
            
        Returns:
            Lista de pacientes que atendem aos filtros
        """
        db = self._load_db()
        pacientes = db.get('pacientes', [])
        
        if not filtro:
            return pacientes
        
        resultados = []
        for paciente in pacientes:
            match = True
            for key, value in filtro.items():
                if key == 'nome':
                    nome = paciente.get('identificacao', {}).get('nome_gestante', '')
                    if value.lower() not in nome.lower():
                        match = False
                        break
                elif key == 'unidade_saude':
                    unidade = paciente.get('identificacao', {}).get('unidade_saude', '')
                    if value.lower() not in unidade.lower():
                        match = False
                        break
                else:
                    # Busca genérica
                    if value not in str(paciente.get(key, '')):
                        match = False
                        break
            
            if match:
                resultados.append(paciente)
        
        return resultados
    
    def obter_todos_pacientes(self) -> List[Dict]:
        """
        Retorna todos os pacientes
        
        Returns:
            Lista com todos os pacientes
        """
        db = self._load_db()
        return db.get('pacientes', [])
    
    def obter_estatisticas(self) -> Dict:
        """
        Retorna estatísticas do banco de dados
        
        Returns:
            Dicionário com estatísticas
        """
        db = self._load_db()
        pacientes = db.get('pacientes', [])
        
        stats = {
            'total_pacientes': len(pacientes),
            'ultima_atualizacao': db.get('ultima_atualizacao', ''),
            'inicio_pre_natal_antes_12s': {'sim': 0, 'nao': 0},
            'consultas_pre_natal': {'ate_6': 0, 'mais_6': 0},
            'vacinas_completas': {'completa': 0, 'incompleta': 0, 'nao_avaliado': 0},
            'plano_parto': {'sim': 0, 'nao': 0},
            'participou_grupos': {'sim': 0, 'nao': 0}
        }
        
        for paciente in pacientes:
            avaliacao = paciente.get('avaliacao', {})
            
            # Início pré-natal antes de 12 semanas
            inicio = avaliacao.get('inicio_pre_natal_antes_12s')
            if inicio is True:
                stats['inicio_pre_natal_antes_12s']['sim'] += 1
            elif inicio is False:
                stats['inicio_pre_natal_antes_12s']['nao'] += 1
            
            # Consultas de pré-natal
            num_consultas = avaliacao.get('consultas_pre_natal', 0)
            if num_consultas >= 6:
                stats['consultas_pre_natal']['mais_6'] += 1
            else:
                stats['consultas_pre_natal']['ate_6'] += 1
            
            # Vacinas completas
            vacina_status = avaliacao.get('vacinas_completas', '').lower()
            if 'completa' in vacina_status or vacina_status == 'completo':
                stats['vacinas_completas']['completa'] += 1
            elif 'incompleta' in vacina_status or vacina_status == 'incompleto':
                stats['vacinas_completas']['incompleta'] += 1
            else:
                stats['vacinas_completas']['nao_avaliado'] += 1
            
            # Plano de parto
            tem_plano = avaliacao.get('plano_parto')
            if tem_plano is True:
                stats['plano_parto']['sim'] += 1
            elif tem_plano is False:
                stats['plano_parto']['nao'] += 1
            
            # Participação em grupos
            participou = avaliacao.get('participou_grupos')
            if participou is True:
                stats['participou_grupos']['sim'] += 1
            elif participou is False:
                stats['participou_grupos']['nao'] += 1
        
        return stats
    
    def obter_estatisticas_temporais(self, filtro: str) -> Dict:
        """
        Retorna estatísticas temporais agrupadas por data para um indicador específico
        
        Args:
            filtro: Nome do indicador (ex: 'inicio_pre_natal_antes_12s')
            
        Returns:
            Dicionário com dados temporais: {datas: [], valores: {}}
        """
        db = self._load_db()
        pacientes = db.get('pacientes', [])
        
        # Agrupar pacientes por data (apenas a data, sem hora)
        pacientes_por_data = {}
        
        for paciente in pacientes:
            data_salvamento = paciente.get('data_salvamento', '')
            if not data_salvamento:
                continue
                
            # Extrair apenas a data (YYYY-MM-DD)
            data_limpa = data_salvamento.split(' ')[0]
            
            if data_limpa not in pacientes_por_data:
                pacientes_por_data[data_limpa] = []
            
            pacientes_por_data[data_limpa].append(paciente)
        
        # Ordenar datas
        datas_ordenadas = sorted(pacientes_por_data.keys())
        
        # Calcular estatísticas para cada data
        resultado = {
            'datas': datas_ordenadas,
            'valores': {}
        }
        
        for data in datas_ordenadas:
            pacientes_da_data = pacientes_por_data[data]
            
            # Calcular estatísticas para este indicador nesta data
            if filtro == 'inicio_pre_natal_antes_12s':
                sim = sum(1 for p in pacientes_da_data if p.get('avaliacao', {}).get('inicio_pre_natal_antes_12s') is True)
                nao = sum(1 for p in pacientes_da_data if p.get('avaliacao', {}).get('inicio_pre_natal_antes_12s') is False)
                total = len(pacientes_da_data)
                resultado['valores'][data] = {
                    'Sim': sim,
                    'Não': nao,
                    'Total': total,
                    'Porcentagem': (sim / total * 100) if total > 0 else 0
                }
            
            elif filtro == 'consultas_pre_natal':
                mais_6 = sum(1 for p in pacientes_da_data if p.get('avaliacao', {}).get('consultas_pre_natal', 0) >= 6)
                ate_6 = sum(1 for p in pacientes_da_data if p.get('avaliacao', {}).get('consultas_pre_natal', 0) < 6)
                total = len(pacientes_da_data)
                resultado['valores'][data] = {
                    '≥ 6 consultas': mais_6,
                    '< 6 consultas': ate_6,
                    'Total': total,
                    'Porcentagem': (mais_6 / total * 100) if total > 0 else 0
                }
            
            elif filtro == 'vacinas_completas':
                completa = sum(1 for p in pacientes_da_data 
                             if 'completa' in p.get('avaliacao', {}).get('vacinas_completas', '').lower() or 
                                p.get('avaliacao', {}).get('vacinas_completas', '').lower() == 'completo')
                incompleta = sum(1 for p in pacientes_da_data 
                               if 'incompleta' in p.get('avaliacao', {}).get('vacinas_completas', '').lower() or 
                                  p.get('avaliacao', {}).get('vacinas_completas', '').lower() == 'incompleto')
                nao_avaliado = sum(1 for p in pacientes_da_data if p.get('avaliacao', {}).get('vacinas_completas', '') == '' or 
                                 not ('completa' in p.get('avaliacao', {}).get('vacinas_completas', '').lower() or 
                                      'incompleta' in p.get('avaliacao', {}).get('vacinas_completas', '').lower()))
                total = len(pacientes_da_data)
                resultado['valores'][data] = {
                    'Completo': completa,
                    'Incompleto': incompleta,
                    'Não avaliado': nao_avaliado,
                    'Total': total,
                    'Porcentagem': (completa / total * 100) if total > 0 else 0
                }
            
            elif filtro == 'plano_parto':
                sim = sum(1 for p in pacientes_da_data if p.get('avaliacao', {}).get('plano_parto') is True)
                nao = sum(1 for p in pacientes_da_data if p.get('avaliacao', {}).get('plano_parto') is False)
                total = len(pacientes_da_data)
                resultado['valores'][data] = {
                    'Sim': sim,
                    'Não': nao,
                    'Total': total,
                    'Porcentagem': (sim / total * 100) if total > 0 else 0
                }
            
            elif filtro == 'participou_grupos':
                sim = sum(1 for p in pacientes_da_data if p.get('avaliacao', {}).get('participou_grupos') is True)
                nao = sum(1 for p in pacientes_da_data if p.get('avaliacao', {}).get('participou_grupos') is False)
                total = len(pacientes_da_data)
                resultado['valores'][data] = {
                    'Participou': sim,
                    'Não participou': nao,
                    'Total': total,
                    'Porcentagem': (sim / total * 100) if total > 0 else 0
                }
        
        return resultado
    
    def deletar_paciente(self, paciente_id: str) -> Dict:
        """
        Deleta um paciente do banco de dados
        
        Args:
            paciente_id: ID do paciente a ser deletado
            
        Returns:
            Dicionário com o resultado da operação
        """
        db = self._load_db()
        
        # Buscar paciente
        paciente_index = None
        for i, paciente in enumerate(db.get('pacientes', [])):
            if paciente.get('id') == paciente_id:
                paciente_index = i
                break
        
        if paciente_index is None:
            return {
                'success': False,
                'message': 'Paciente não encontrado'
            }
        
        # Remover paciente
        paciente_removido = db['pacientes'].pop(paciente_index)
        db['total_pacientes'] = len(db['pacientes'])
        db['ultima_atualizacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self._save_db(db)
        
        # Tentar remover arquivo individual se existir
        if 'arquivo_origem' in paciente_removido:
            arquivo_origem = paciente_removido['arquivo_origem']
            filepath = os.path.join(self.pacientes_dir, arquivo_origem)
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception:
                    pass  # Ignora erro se não conseguir remover o arquivo
        
        return {
            'success': True,
            'message': 'Paciente deletado com sucesso'
        }
    
    def criar_backup(self) -> Dict:
        """
        Cria um backup completo do banco de dados
        
        Returns:
            Dicionário com o backup completo
        """
        db = self._load_db()
        return {
            'success': True,
            'backup': db.copy(),
            'data_backup': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def restaurar_backup(self, backup_data: Dict) -> Dict:
        """
        Restaura o banco de dados a partir de um backup
        
        Args:
            backup_data: Dicionário com os dados do backup
            
        Returns:
            Dicionário com o resultado da operação
        """
        try:
            # Validar estrutura do backup
            if 'pacientes' not in backup_data or not isinstance(backup_data['pacientes'], list):
                return {
                    'success': False,
                    'message': 'Estrutura do backup inválida'
                }
            
            # Salvar backup como banco de dados
            db_backup = {
                'pacientes': backup_data.get('pacientes', []),
                'total_pacientes': len(backup_data.get('pacientes', [])),
                'ultima_atualizacao': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Salvar no arquivo
            self._save_db(db_backup)
            
            return {
                'success': True,
                'message': 'Backup restaurado com sucesso',
                'total_pacientes': db_backup['total_pacientes']
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao restaurar backup: {str(e)}'
            }
    
    def limpar_todos_dados(self) -> Dict:
        """
        Remove todos os dados do banco de dados
        
        Returns:
            Dicionário com o resultado da operação
        """
        try:
            empty_db = {
                'pacientes': [],
                'ultima_atualizacao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_pacientes': 0
            }
            self._save_db(empty_db)
            
            return {
                'success': True,
                'message': 'Todos os dados foram excluídos com sucesso'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao limpar dados: {str(e)}'
            }


# Instância global do banco de dados
db = Database()
