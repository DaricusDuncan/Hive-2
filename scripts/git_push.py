import os
import subprocess

def configure_git():
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN not found in environment")
        return False
    
    try:
        # Initialize Git if not already initialized
        subprocess.run(['git', 'init'], check=True)
        
        # Configure Git user
        subprocess.run(['git', 'config', '--global', 'user.email', "agent@example.com"], check=True)
        subprocess.run(['git', 'config', '--global', 'user.name', "Replit Agent"], check=True)
        
        # Configure Git credentials
        subprocess.run(['git', 'config', '--global', 'credential.helper', 'store'], check=True)
        
        # Set up the remote repository URL with token
        remote_url = "https://github.com/DaricusDuncan/Hive-2"
        token_url = f'https://oauth2:{token}@github.com/DaricusDuncan/Hive-2'
        
        # Remove existing remote if any
        subprocess.run(['git', 'remote', 'remove', 'origin'], check=False)
        
        # Add new remote with token
        subprocess.run(['git', 'remote', 'add', 'origin', token_url], check=True)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error configuring git: {str(e)}")
        return False

def push_changes():
    try:
        if not configure_git():
            return False
        
        # Add all changes
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Commit changes with a conventional commit message
        subprocess.run(['git', 'commit', '-m', 'chore(config): set up git configuration and resolve push issues'], check=True)
        
        # Push changes to main branch
        subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error pushing changes: {str(e)}")
        return False

if __name__ == "__main__":
    success = push_changes()
    exit(0 if success else 1)
