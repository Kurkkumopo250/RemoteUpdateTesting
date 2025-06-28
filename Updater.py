import requests
import json
import os

def update_files_from_github(repo_url, manifest_path, local_dir, branch='main'):
    """
    Fetches updated files from a GitHub repository based on a manifest file with an overall application version.
    
    Args:
        repo_url (str): Base URL of the GitHub repository (e.g., 'https://api.github.com/repos/username/repo')
        manifest_path (str): Path to the manifest file in the repository (e.g., 'manifest.json')
        local_dir (str): Local directory to store files and manifest
        branch (str): Repository branch to fetch from (default: 'main')
    
    Returns:
        dict: Status of update operation including updated files and errors
    """
    try:
        os.makedirs(local_dir, exist_ok=True)
        remote_manifest_url = f"{repo_url}/contents/{manifest_path}?ref={branch}"
        headers = {'Accept': 'application/vnd.github.v3+json'}
        response = requests.get(remote_manifest_url, headers=headers)
        response.raise_for_status()
        
        remote_manifest_data = response.json()
        remote_manifest_content = requests.get(remote_manifest_data['download_url']).json()
        
        local_manifest_path = os.path.join(local_dir, manifest_path)
        local_manifest = {'version': '0.0.0', 'files': []}
        if os.path.exists(local_manifest_path):
            with open(local_manifest_path, 'r') as f:
                local_manifest = json.load(f)
        
        updated_files = []
        errors = []
        
        remote_version = remote_manifest_content.get('version', '0.0.0')
        local_version = local_manifest.get('version', '0.0.0')
        
        if remote_version != local_version:
            for file_path in remote_manifest_content.get('files', []):
                try:
                    file_url = f"{repo_url}/contents/{file_path}?ref={branch}"
                    file_response = requests.get(file_url, headers=headers)
                    file_response.raise_for_status()
                    
                    file_data = file_response.json()
                    file_content = requests.get(file_data['download_url']).content
                    
                    local_file_path = os.path.join(local_dir, file_path)
                    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                    with open(local_file_path, 'wb') as f:
                        f.write(file_content)
                    
                    updated_files.append(file_path)
                except Exception as e:
                    errors.append(f"Failed to update {file_path}: {str(e)}")
        
            if updated_files and not errors:
                with open(local_manifest_path, 'w') as f:
                    json.dump(remote_manifest_content, f, indent=2)
        else:
            return {
                'status': 'no_update_needed',
                'updated_files': [],
                'errors': []
            }
        
        return {
            'status': 'success' if not errors else 'partial' if updated_files else 'failed',
            'updated_files': updated_files,
            'errors': errors
        }
    
    except Exception as e:
        return {
            'status': 'failed',
            'updated_files': [],
            'errors': [f"Update failed: {str(e)}"]
        }