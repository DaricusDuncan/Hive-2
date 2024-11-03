import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from app import create_app
from core.database import db
from services.github import GitHubService
from urllib.parse import urlparse

def analyze_simpleapi():
    """Analyze the SimpleAPI GitHub repository"""
    app = create_app()
    with app.app_context():
        try:
            # Initialize GitHub service
            github_service = GitHubService()
            repo_url = "https://github.com/DaricusDuncan/SimpleAPI"
            
            # Parse repository URL
            parsed_url = urlparse(repo_url)
            path_parts = [p for p in parsed_url.path.split('/') if p]
            
            if len(path_parts) < 2:
                print("Invalid repository URL format")
                return False
            
            owner, repo_name = path_parts[0], path_parts[1]
            print(f"\nAnalyzing repository: {owner}/{repo_name}")
            
            # Test repository access
            try:
                repo = github_service.client.get_repo(f"{owner}/{repo_name}")
                print(f"Successfully accessed repository: {repo.full_name}")
            except Exception as e:
                print(f"Error accessing repository: {str(e)}")
                return False
            
            # Analyze repository issues
            issues = github_service.prioritize_issues(owner, repo_name)
            
            if issues:
                print("\nRepository Analysis Results:")
                print(f"Total issues analyzed: {len(issues)}")
                
                # Print detailed analysis for each issue
                for i, issue in enumerate(issues, 1):
                    print(f"\nIssue #{i}:")
                    print(f"Number: #{issue['issue_number']}")
                    print(f"Title: {issue['title']}")
                    print(f"Complexity: {issue['complexity']}/10")
                    print(f"Score: {issue['score']}")
                    print(f"Implementation Time: {issue['implementation_time']} hours")
                    print(f"Security Impact: {issue['security_impact']}/10")
                    print(f"Performance Impact: {issue['performance_impact']}/10")
                    print(f"UX Impact: {issue['ux_impact']}/10")
                    print("\nDependencies:")
                    if issue['dependencies']:
                        for dep in issue['dependencies']:
                            print(f"- #{dep['issue_number']}: {dep['title']} ({dep['state']})")
                    else:
                        print("- No dependencies")
                print("\nAnalysis completed successfully!")
                return True
            else:
                print("No open issues found in the repository")
                return True
                
        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            return False

if __name__ == '__main__':
    success = analyze_simpleapi()
    sys.exit(0 if success else 1)
