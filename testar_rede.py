import time
import socket
import ctypes
import sys
import os
from inicio.rede.zeroconf_discovery import start_zeroconf, get_discovered_servers, stop_zeroconf
from inicio.rede.leader import get_local_ip

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def test_zeroconf_discovery():
    if not is_admin():
        print("Solicitando privilégios de Administrador...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return

    print("--- Teste de Localização de Servidor (Zeroconf) - MODO ADM ---")
    
    local_ip = get_local_ip()
    test_port = 5000
    
    print(f"IP Local: {local_ip}")
    print(f"Iniciando anúncio Zeroconf na porta {test_port}...")
    
    try:
        start_zeroconf(test_port)
        print(f"Aguardando 10 segundos para propagação mDNS e descoberta...")
        
        # Loop mais longo para dar tempo ao Windows/Rede
        for i in range(10):
            time.sleep(1)
            peers = get_discovered_servers()
            print(f"Segundo {i+1}: {len(peers)} servidor(es) em cache.")
            for p in peers:
                suffix = " (VOCÊ)" if p['ip'] == local_ip and p['port'] == test_port else ""
                print(f"  - {p['hostname']} em {p['ip']}:{p['port']}{suffix}")
        
        final_peers = get_discovered_servers()
        print(f"\nResultado Final: {len(final_peers)} servidor(es) detectado(s).")
        
        if not final_peers:
            print("Nenhum outro servidor foi encontrado além deste (se anunciado).")
        else:
            print("Servidores encontrados:")
            for p in final_peers:
                print(f"  > IP: {p['ip']} | Porta: {p['port']} | Hostname: {p['hostname']}")

    except KeyboardInterrupt:
        print("\nTeste interrompido pelo usuário.")
    except Exception as e:
        print(f"\nErro durante o teste: {e}")
    finally:
        print("\nFinalizando Zeroconf...")
        stop_zeroconf()
        print("Teste concluído.")

if __name__ == "__main__":
    test_zeroconf_discovery()
