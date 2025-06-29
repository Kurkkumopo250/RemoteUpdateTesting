import requests
import json
import os

def check_updates_available(repo_url, manifest_path, local_dir, branch='main', github_token=None):
    """
    Checks if updates are available by comparing remote and local manifest versions.
    
    Args:
        repo_url (str): Base URL of the GitHub repository (e.g., 'https://api.github.com/repos/username/repo')
        manifest_path (str): Path to the manifest file in the repository (e.g., 'manifest.json')
        local_dir (str): Local directory where manifest is stored
        branch (str): Repository branch to fetch from (default: 'main')
        github_token (str, optional): GitHub Personal Access Token for private repositories
    
    Returns:
        dict: Result indicating if update is available, remote version, and any errors
    """
    try:
        os.makedirs(local_dir, exist_ok=True)
        remote_manifest_url = f"{repo_url}/contents/{manifest_path}?ref={branch}"
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if github_token:
            headers['Authorization'] = f'Bearer {github_token}'
        
        print(f"Checking manifest at: {remote_manifest_url}")
        response = requests.get(remote_manifest_url, headers=headers)
        if response.status_code == 404:
            error_msg = f"Manifest file not found at {remote_manifest_url}"
            print(f"Error: {error_msg} (HTTP 404)")
            return {
                'update_available': False,
                'remote_version': None,
                'errors': [error_msg]
            }
        elif response.status_code == 403:
            error_msg = "Access forbidden. Check repository permissions or provide a valid GitHub token."
            print(f"Error: {error_msg} (HTTP 403)")
            return {
                'update_available': False,
                'remote_version': None,
                'errors': [error_msg]
            }
        response.raise_for_status()
        
        remote_manifest_data = response.json()
        print(f"Fetching manifest content from: {remote_manifest_data['download_url']}")
        manifest_response = requests.get(remote_manifest_data['download_url'], headers=headers)
        if manifest_response.status_code != 200:
            error_msg = f"Failed to fetch manifest content from {remote_manifest_data['download_url']} (HTTP {manifest_response.status_code})"
            print(f"Error: {error_msg}")
            return {
                'update_available': False,
                'remote_version': None,
                'errors': [error_msg]
            }
        remote_manifest_content = manifest_response.json()
        
        local_manifest_path = os.path.join(local_dir, manifest_path)
        local_manifest = {'version': '0.0.0'}
        if os.path.exists(local_manifest_path):
            with open(local_manifest_path, 'r') as f:
                local_manifest = json.load(f)
        
        remote_version = remote_manifest_content.get('version', '0.0.0')
        local_version = local_manifest.get('version', '0.0.0')
        print(f"Remote version: {remote_version}, Local version: {local_version}")
        
        return {
            'update_available': remote_version != local_version,
            'remote_version': remote_version,
            'errors': []
        }
    
    except Exception as e:
        error_msg = f"Update check failed: {str(e)}"
        print(f"Error: {error_msg}")
        return {
            'update_available': False,
            'remote_version': None,
            'errors': [error_msg]
        }

def update_files_from_github(repo_url, manifest_path, local_dir, branch='main', github_token=None):
    """
    Fetches updated files from a GitHub repository based on a manifest file with an overall application version.
    
    Args:
        repo_url (str): Base URL of the GitHub repository (e.g., 'https://api.github.com/repos/username/repo')
        manifest_path (str): Path to the manifest file in the repository (e.g., 'manifest.json')
        local_dir (str): Local directory to store files and manifest
        branch (str): Repository branch to fetch from (default: 'main')
        github_token (str, optional): GitHub Personal Access Token for private repositories
    
    Returns:
        dict: Status of update operation including updated files and errors
    """
    try:
        os.makedirs(local_dir, exist_ok=True)
        remote_manifest_url = f"{repo_url}/contents/{manifest_path}?ref={branch}"
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if github_token:
            headers['Authorization'] = f'Bearer {github_token}'
        
        print(f"Fetching manifest from: {remote_manifest_url}")
        response = requests.get(remote_manifest_url, headers=headers)
        if response.status_code == 404:
            error_msg = f"Manifest file not found at {remote_manifest_url}"
            print(f"Error: {error_msg} (HTTP 404)")
            return {
                'status': 'failed',
                'updated_files': [],
                'errors': [error_msg]
            }
        elif response.status_code == 403:
            error_msg = "Access forbidden. Check repository permissions or provide a valid GitHub token."
            print(f"Error: {error_msg} (HTTP 403)")
            return {
                'status': 'failed',
                'updated_files': [],
                'errors': [error_msg]
            }
        response.raise_for_status()
        
        remote_manifest_data = response.json()
        print(f"Manifest data retrieved: {remote_manifest_data['download_url']}")
        manifest_response = requests.get(remote_manifest_data['download_url'], headers=headers)
        if manifest_response.status_code != 200:
            error_msg = f"Failed to fetch manifest content from {remote_manifest_data['download_url']} (HTTP {manifest_response.status_code})"
            print(f"Error: {error_msg}")
            return {
                'status': 'failed',
                'updated_files': [],
                'errors': [error_msg]
            }
        remote_manifest_content = manifest_response.json()
        
        local_manifest_path = os.path.join(local_dir, manifest_path)
        local_manifest = {'version': '0.0.0', 'files': []}
        if os.path.exists(local_manifest_path):
            with open(local_manifest_path, 'r') as f:
                local_manifest = json.load(f)
        
        updated_files = []
        errors = []
        
        remote_version = remote_manifest_content.get('version', '0.0.0')
        local_version = local_manifest.get('version', '0.0.0')
        print(f"Remote version: {remote_version}, Local version: {local_version}")
        
        if remote_version != local_version:
            for file_path in remote_manifest_content.get('files', []):
                try:
                    file_url = f"{repo_url}/contents/{file_path}?ref={branch}"
                    print(f"Fetching file: {file_url}")
                    file_response = requests.get(file_url, headers=headers)
                    if file_response.status_code != 200:
                        error_msg = f"Failed to fetch file {file_path} from {file_url} (HTTP {file_response.status_code})"
                        print(f"Error: {error_msg}")
                        errors.append(error_msg)
                        continue
                    
                    file_data = file_response.json()
                    print(f"Downloading file content from: {file_data['download_url']}")
                    file_content = requests.get(file_data['download_url'], headers=headers).content
                    
                    local_file_path = os.path.join(local_dir, file_path)
                    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                    with open(local_file_path, 'wb') as f:
                        f.write(file_content)
                    print(f"Successfully updated file: {local_file_path}")
                    
                    updated_files.append(file_path)
                except Exception as e:
                    error_msg = f"Failed to update {file_path}: {str(e)}"
                    print(f"Error: {error_msg}")
                    errors.append(error_msg)
        
            if updated_files and not errors:
                print(f"Updating local manifest at: {local_manifest_path}")
                with open(local_manifest_path, 'w') as f:
                    json.dump(remote_manifest_content, f, indent=2)
        else:
            print("No update needed: Remote evenings are the same")
            return {
                'status': 'no_update_needed',
                'updated_files': [],
                'errors': []
            }
        
        status = 'success' if not errors else 'partial' if updated_files else 'failed'
        print(f"Update completed with status: {status}")
        return {
            'status': status,
            'updated_files': updated_files,
            'errors': errors
        }
    
    except Exception as e:
        error_msg = f"Update failed: {str(e)}"
        print(f"Error: {error_msg}")
        return {
            'status': 'failed',
            'updated_files': [],
            'errors': [error_msg]
        }