#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Link Checker para Portafolio

Este script recorre todos los archivos del proyecto y verifica si hay enlaces rotos.
Busca URLs en archivos HTML, Astro, Markdown, JSON y otros formatos de texto.
"""

import os
import re
import json
import requests
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import time
import argparse
import datetime

# Colores para la terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Cargar patrones de URLs a ignorar desde el archivo JSON
def load_ignore_patterns():
    try:
        ignore_file = Path(__file__).parent / 'ignore_urls.json'
        if ignore_file.exists():
            with open(ignore_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('ignore_patterns', [])
    except Exception as e:
        print(f"Error al cargar patrones de URLs a ignorar: {e}")
    
    # Patrones por defecto si no se puede cargar el archivo
    return [
        'https://cdn-lfs-us-1.huggingface.co/repos',
        'openai/dall-e-3.png',
        'https://wa.me/',
        'wa.me/'
    ]

# Configuración
class Config:
    # Extensiones de archivos a revisar
    FILE_EXTENSIONS = [
        '.html', '.astro', '.md', '.mdx', '.json', '.js', '.jsx', '.ts', '.tsx', '.css'
    ]
    
    # Directorios a ignorar
    IGNORE_DIRS = [
        'node_modules', '.git', '.astro', 'dist', 'public/fonts'
    ]
    
    # Archivos específicos a ignorar
    IGNORE_FILES = [
        'link_checker_README.md',
        'link_checker_results.json',
        'link_checker_report.html',
        'ignore_urls.json',
        'src/pages/html.astro',
        'README.md'
    ]
    
    # Patrones de archivos a ignorar (expresiones regulares)
    IGNORE_FILE_PATTERNS = [
        r'^link_checker_.*\.md$',  # Todos los archivos MD que empiecen con link_checker_
        r'.*\.min\.js$',           # Archivos JavaScript minificados
        r'.*\.test\.(js|ts)$'      # Archivos de prueba
    ]
    
    # Tiempo de espera para las solicitudes HTTP (en segundos)
    TIMEOUT = 5
    
    # Número máximo de hilos para las solicitudes concurrentes
    MAX_WORKERS = 10
    
    # Patrones para encontrar URLs en archivos
    URL_PATTERNS = [
        # HTML/Astro href y src
        r'href=[\'"]([^\'"]+)[\'"]',
        r'src=[\'"]([^\'"]+)[\'"]',
        # URLs en Markdown
        r'\[.*?\]\((https?://[^\s\)]+)\)',
        # URLs en texto plano o código
        r'https?://[^\s\'"<>]+',
        # URLs en JSON
        r'"url":\s*"(https?://[^"]+)"',
        r'"link":\s*"(https?://[^"]+)"',
    ]
    
    # Patrones de URLs a ignorar por defecto (se cargarán desde el archivo JSON)
    IGNORE_URL_PATTERNS = load_ignore_patterns()

class LinkChecker:
    def __init__(self, base_dir, verbose=False, check_internal=True, ignore_patterns=None, no_html=False):
        self.base_dir = Path(base_dir)
        self.verbose = verbose
        self.check_internal = check_internal
        self.ignore_patterns = ignore_patterns or Config.IGNORE_URL_PATTERNS
        self.no_html = no_html
        self.ignore_files = Config.IGNORE_FILES.copy()
        self.checked_urls = {}  # Cache para evitar verificar la misma URL varias veces
        self.internal_paths = set()  # Conjunto de rutas internas válidas
        self.broken_links = []  # Lista de enlaces rotos encontrados
        
        # Estadísticas
        self.stats = {
            'total_files': 0,
            'total_links': 0,
            'broken_links': 0,
            'ok_links': 0,
            'skipped_links': 0
        }
    
    def log(self, message, level='info'):
        """Imprime mensajes según el nivel de verbosidad"""
        if not self.verbose and level == 'debug':
            return
            
        prefix = {
            'info': f"{Colors.OKBLUE}[INFO]{Colors.ENDC}",
            'debug': f"{Colors.HEADER}[DEBUG]{Colors.ENDC}",
            'warning': f"{Colors.WARNING}[ADVERTENCIA]{Colors.ENDC}",
            'error': f"{Colors.FAIL}[ERROR]{Colors.ENDC}",
            'success': f"{Colors.OKGREEN}[ÉXITO]{Colors.ENDC}"
        }.get(level, '')
        
        print(f"{prefix} {message}")
    
    def collect_internal_paths(self):
        """Recopila todas las rutas internas válidas del proyecto"""
        self.log("Recopilando rutas internas válidas...", 'info')
        
        for root, dirs, files in os.walk(self.base_dir):
            # Filtrar directorios ignorados
            dirs[:] = [d for d in dirs if d not in Config.IGNORE_DIRS]
            
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.base_dir)
                
                # Agregar la ruta relativa al conjunto de rutas internas
                self.internal_paths.add(str(rel_path))
                
                # Agregar rutas sin extensión para páginas
                if file.endswith(('.astro', '.html', '.md', '.mdx')):
                    path_without_ext = str(rel_path.with_suffix(''))
                    self.internal_paths.add(path_without_ext)
                    
                    # Para archivos index, agregar también la ruta del directorio
                    if file.startswith('index.'):
                        dir_path = str(rel_path.parent)
                        if dir_path:
                            self.internal_paths.add(dir_path)
                            self.internal_paths.add(f"{dir_path}/")
        
        self.log(f"Se encontraron {len(self.internal_paths)} rutas internas válidas", 'debug')
    
    def is_valid_internal_path(self, path):
        """Verifica si una ruta interna es válida"""
        # Normalizar la ruta
        path = path.lstrip('/')
        
        # Comprobar si la ruta existe en nuestro conjunto de rutas internas
        if path in self.internal_paths:
            return True
            
        # Comprobar si existe como archivo en public/
        public_path = self.base_dir / 'public' / path
        if public_path.exists():
            return True
            
        # Comprobar si existe como archivo en src/
        src_path = self.base_dir / 'src' / path
        if src_path.exists():
            return True
            
        return False
    
    def should_ignore_url(self, url):
        """Verifica si una URL debe ser ignorada según los patrones configurados"""
        # Ignorar anclas y enlaces de correo electrónico
        if url.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
            return True
            
        # Verificar patrones de URLs a ignorar
        for pattern in self.ignore_patterns:
            if pattern in url:
                self.log(f"Ignorando URL que coincide con patrón '{pattern}': {url}", 'debug')
                return True
        
        self.log(f"No se ignoró la URL: {url}", 'debug')
        return False
    
    def check_url(self, url, source_file):
        """Verifica si una URL es válida"""
        # Si ya hemos verificado esta URL, devolver el resultado en caché
        if url in self.checked_urls:
            return self.checked_urls[url]
            
        # Verificar si la URL debe ser ignorada
        if self.should_ignore_url(url):
            self.stats['skipped_links'] += 1
            self.checked_urls[url] = True
            return True
            
        # Analizar la URL
        parsed_url = urlparse(url)
        
        # Verificar enlaces internos
        if not parsed_url.netloc:
            if not self.check_internal:
                self.stats['skipped_links'] += 1
                return True
                
            # Obtener la ruta sin el fragmento
            path = parsed_url.path
            if path.startswith('/'):
                path = path[1:]
                
            is_valid = self.is_valid_internal_path(path)
            self.checked_urls[url] = is_valid
            
            if not is_valid:
                self.stats['broken_links'] += 1
                self.broken_links.append({
                    'url': url,
                    'source': source_file,
                    'reason': 'Ruta interna no encontrada'
                })
                return False
            else:
                self.stats['ok_links'] += 1
                return True
        
        # Verificar enlaces externos
        try:
            # Realizar una solicitud HEAD para verificar si la URL existe
            response = requests.head(url, timeout=Config.TIMEOUT, allow_redirects=True)
            
            # Si la solicitud HEAD falla, intentar con GET
            if response.status_code >= 400:
                response = requests.get(url, timeout=Config.TIMEOUT, stream=True, allow_redirects=True)
                response.close()  # Cerrar la conexión inmediatamente
                
            is_valid = response.status_code < 404 or response.status_code >= 900
            self.checked_urls[url] = is_valid
            
            if not is_valid:
                self.stats['broken_links'] += 1
                self.broken_links.append({
                    'url': url,
                    'source': source_file,
                    'reason': f'Código de estado HTTP: {response.status_code}'
                })
                return False
            else:
                self.stats['ok_links'] += 1
                return True
                
        except requests.RequestException as e:
            self.stats['broken_links'] += 1
            self.broken_links.append({
                'url': url,
                'source': source_file,
                'reason': str(e)
            })
            self.checked_urls[url] = False
            return False
    
    def extract_urls_from_file(self, file_path):
        """Extrae URLs de un archivo"""
        urls = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Buscar URLs según los patrones definidos
            for pattern in Config.URL_PATTERNS:
                matches = re.finditer(pattern, content)
                for match in matches:
                    # Obtener la URL del grupo de captura si existe, de lo contrario usar la coincidencia completa
                    if match.groups():
                        url = match.group(1)
                    else:
                        url = match.group(0)
                        
                    # Limpiar la URL
                    url = url.strip()
                    
                    # Agregar la URL a la lista si no está vacía
                    if url and url not in urls:
                        urls.append(url)
        
        except Exception as e:
            self.log(f"Error al leer el archivo {file_path}: {e}", 'error')
        
        return urls
    
    def check_file(self, file_path):
        """Verifica los enlaces en un archivo"""
        rel_path = file_path.relative_to(self.base_dir)
        self.log(f"Verificando enlaces en {rel_path}...", 'debug')
        
        # Extraer URLs del archivo
        urls = self.extract_urls_from_file(file_path)
        self.stats['total_links'] += len(urls)
        
        # Verificar cada URL
        for url in urls:
            self.check_url(url, str(rel_path))
    
    def should_ignore_file(self, file_path):
        """Verifica si un archivo debe ser ignorado"""
        file_name = file_path.name
        
        # Verificar si el archivo está en la lista de archivos a ignorar
        if file_name in self.ignore_files:
            self.log(f"Ignorando archivo: {file_path}", 'debug')
            return True
            
        # Verificar si el archivo coincide con algún patrón a ignorar
        for pattern in Config.IGNORE_FILE_PATTERNS:
            if re.match(pattern, file_name):
                self.log(f"Ignorando archivo que coincide con patrón '{pattern}': {file_path}", 'debug')
                return True
                
        return False
    
    def run(self):
        """Ejecuta el verificador de enlaces"""
        start_time = time.time()
        self.log(f"Iniciando verificación de enlaces en {self.base_dir}...", 'info')
        
        # Mostrar patrones de URLs ignorados
        if self.ignore_patterns:
            self.log(f"Ignorando URLs que coincidan con los siguientes patrones:", 'info')
            for pattern in self.ignore_patterns:
                self.log(f"  - {pattern}", 'info')
        
        # Recopilar rutas internas válidas si se van a verificar enlaces internos
        if self.check_internal:
            self.collect_internal_paths()
        
        # Recorrer todos los archivos del proyecto
        files_to_check = []
        
        for root, dirs, files in os.walk(self.base_dir):
            # Filtrar directorios ignorados
            dirs[:] = [d for d in dirs if d not in Config.IGNORE_DIRS]
            
            for file in files:
                file_path = Path(root) / file
                
                # Verificar solo archivos con extensiones específicas y que no deban ser ignorados
                if any(file.endswith(ext) for ext in Config.FILE_EXTENSIONS) and not self.should_ignore_file(file_path):
                    files_to_check.append(file_path)
        
        self.stats['total_files'] = len(files_to_check)
        self.log(f"Se encontraron {self.stats['total_files']} archivos para verificar", 'info')
        
        # Verificar los archivos en paralelo
        with ThreadPoolExecutor(max_workers=Config.MAX_WORKERS) as executor:
            executor.map(self.check_file, files_to_check)
        
        # Mostrar resultados
        elapsed_time = time.time() - start_time
        self.log(f"Verificación completada en {elapsed_time:.2f} segundos", 'info')
        self.log(f"Archivos verificados: {self.stats['total_files']}", 'info')
        self.log(f"Enlaces encontrados: {self.stats['total_links']}", 'info')
        self.log(f"Enlaces correctos: {self.stats['ok_links']}", 'success')
        self.log(f"Enlaces omitidos: {self.stats['skipped_links']}", 'info')
        self.log(f"Enlaces rotos: {self.stats['broken_links']}", 'warning' if self.stats['broken_links'] > 0 else 'info')
        
        # Mostrar enlaces rotos
        if self.broken_links:
            self.log("Enlaces rotos encontrados:", 'error')
            
            # Agrupar enlaces rotos por archivo
            broken_links_by_file = {}
            for link in self.broken_links:
                file_path = link['source']
                if file_path not in broken_links_by_file:
                    broken_links_by_file[file_path] = []
                broken_links_by_file[file_path].append(link)
            
            # Mostrar enlaces rotos agrupados por archivo
            for file_path, links in broken_links_by_file.items():
                print(f"\n{Colors.BOLD}{Colors.UNDERLINE}Archivo: {file_path}{Colors.ENDC}")
                for i, link in enumerate(links, 1):
                    print(f"  {Colors.FAIL}{i}. URL: {link['url']}{Colors.ENDC}")
                    print(f"     Razón: {link['reason']}")
        else:
            self.log("¡No se encontraron enlaces rotos!", 'success')
        
        # Guardar resultados en un archivo JSON
        self.save_results()
        
        return self.stats['broken_links'] == 0
    
    def save_results(self):
        """Guarda los resultados en un archivo JSON"""
        # Agrupar enlaces rotos por archivo para el reporte JSON
        broken_links_by_file = {}
        for link in self.broken_links:
            file_path = link['source']
            if file_path not in broken_links_by_file:
                broken_links_by_file[file_path] = []
            broken_links_by_file[file_path].append({
                'url': link['url'],
                'reason': link['reason']
            })
        
        results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'stats': self.stats,
            'broken_links': self.broken_links,
            'broken_links_by_file': broken_links_by_file,
            'ignored_patterns': self.ignore_patterns
        }
        
        output_file = self.base_dir / 'link_checker_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        self.log(f"Resultados guardados en {output_file}", 'info')
        
        # Generar reporte HTML si hay enlaces rotos y no se ha desactivado
        if self.broken_links and not self.no_html:
            self.generate_html_report(results)
    
    def generate_html_report(self, results):
        """Genera un reporte HTML con los resultados"""
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        output_file = self.base_dir / 'link_checker_report.html'
        
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Enlaces Rotos - {timestamp}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        .summary {{
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
            border-left: 5px solid #4CAF50;
        }}
        .summary.has-errors {{
            border-left-color: #e74c3c;
        }}
        .file-section {{
            margin-bottom: 30px;
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow: hidden;
        }}
        .file-header {{
            background-color: #f1f1f1;
            padding: 10px 15px;
            font-weight: bold;
            border-bottom: 1px solid #ddd;
        }}
        .link-list {{
            padding: 0;
        }}
        .link-item {{
            list-style: none;
            padding: 15px;
            border-bottom: 1px solid #eee;
        }}
        .link-item:last-child {{
            border-bottom: none;
        }}
        .link-url {{
            font-family: monospace;
            word-break: break-all;
            background-color: #f8f9fa;
            padding: 5px;
            border-radius: 3px;
        }}
        .link-reason {{
            color: #e74c3c;
            margin-top: 5px;
        }}
        .stats-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        .stats-table th, .stats-table td {{
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .stats-table th {{
            background-color: #f1f1f1;
        }}
        .ignored-patterns {{
            background-color: #f8f9fa;
            padding: 10px 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .ignored-patterns ul {{
            margin: 5px 0 0 0;
            padding-left: 20px;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-style: italic;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <h1>Reporte de Enlaces Rotos</h1>
    
    <div class="summary {{'has-errors' if results['stats']['broken_links'] > 0 else ''}}">
        <h2>Resumen</h2>
        <table class="stats-table">
            <tr>
                <th>Archivos verificados</th>
                <td>{results['stats']['total_files']}</td>
            </tr>
            <tr>
                <th>Enlaces encontrados</th>
                <td>{results['stats']['total_links']}</td>
            </tr>
            <tr>
                <th>Enlaces correctos</th>
                <td>{results['stats']['ok_links']}</td>
            </tr>
            <tr>
                <th>Enlaces omitidos</th>
                <td>{results['stats']['skipped_links']}</td>
            </tr>
            <tr>
                <th>Enlaces rotos</th>
                <td>{results['stats']['broken_links']}</td>
            </tr>
        </table>
    </div>
    
    <div class="ignored-patterns">
        <h3>Patrones de URLs ignorados</h3>
        <ul>
"""
        
        for pattern in results['ignored_patterns']:
            html += f"            <li>{pattern}</li>\n"
            
        html += """        </ul>
    </div>
    
    <h2>Enlaces rotos por archivo</h2>
"""
        
        if not results['broken_links_by_file']:
            html += """    <p>¡No se encontraron enlaces rotos! 🎉</p>"""
        else:
            for file_path, links in results['broken_links_by_file'].items():
                html += f"""    <div class="file-section">
        <div class="file-header">{file_path}</div>
        <ul class="link-list">
"""
                
                for i, link in enumerate(links, 1):
                    html += f"""            <li class="link-item">
                <div><strong>{i}.</strong> <span class="link-url">{link['url']}</span></div>
                <div class="link-reason">Razón: {link['reason']}</div>
            </li>
"""
                
                html += """        </ul>
    </div>
"""
        
        html += f"""    <p class="timestamp">Reporte generado el {timestamp}</p>
</body>
</html>"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
            
        self.log(f"Reporte HTML generado en {output_file}", 'info')

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Verificador de enlaces para proyectos web')
    parser.add_argument('--dir', '-d', default='.', help='Directorio base del proyecto')
    parser.add_argument('--verbose', '-v', action='store_true', help='Mostrar información detallada')
    parser.add_argument('--skip-internal', '-s', action='store_true', help='Omitir verificación de enlaces internos')
    parser.add_argument('--ignore', '-i', action='append', help='Patrones de URLs a ignorar (puede especificarse múltiples veces)')
    parser.add_argument('--ignore-file', '-f', action='append', help='Archivos adicionales a ignorar (puede especificarse múltiples veces)')
    parser.add_argument('--no-html', action='store_true', help='No generar reporte HTML')
    
    args = parser.parse_args()
    
    # Combinar patrones de ignorar por defecto con los especificados por el usuario
    ignore_patterns = Config.IGNORE_URL_PATTERNS.copy()
    if args.ignore:
        ignore_patterns.extend(args.ignore)
    
    # Combinar archivos a ignorar por defecto con los especificados por el usuario
    ignore_files = Config.IGNORE_FILES.copy()
    if args.ignore_file:
        ignore_files.extend(args.ignore_file)
    
    checker = LinkChecker(
        base_dir=args.dir,
        verbose=args.verbose,
        check_internal=not args.skip_internal,
        ignore_patterns=ignore_patterns,
        no_html=args.no_html
    )
    
    # Establecer archivos adicionales a ignorar
    checker.ignore_files = ignore_files
    
    success = checker.run()
    
    # Salir con código de error si se encontraron enlaces rotos
    if not success:
        exit(1)

if __name__ == '__main__':
    main() 