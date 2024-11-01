from github import Github
import os
from datetime import datetime, timedelta
import re
from collections import defaultdict
import numpy as np
from functools import lru_cache

class GitHubService:
    def __init__(self):
        self.client = Github(os.environ.get('GITHUB_TOKEN'))
        self._security_keywords = {'security', 'vulnerability', 'exploit', 'csrf', 'xss', 'injection', 'authentication'}
        self._performance_keywords = {'performance', 'optimization', 'slow', 'memory', 'cpu', 'latency', 'bottleneck'}
        self._ux_keywords = {'usability', 'user experience', 'ux', 'ui', 'interface', 'accessibility', 'responsive'}
    
    @lru_cache(maxsize=100)
    def get_user_info(self):
        """Get authenticated user information"""
        user = self.client.get_user()
        return {
            'login': user.login,
            'name': user.name,
            'email': user.email,
            'public_repos': user.public_repos,
            'followers': user.followers,
            'following': user.following
        }
    
    @lru_cache(maxsize=100)
    def list_repositories(self, username=None):
        """List repositories for a user or authenticated user"""
        if username:
            user = self.client.get_user(username)
            repos = user.get_repos()
        else:
            repos = self.client.get_user().get_repos()
            
        return [{
            'name': repo.name,
            'description': repo.description,
            'url': repo.html_url,
            'stars': repo.stargazers_count,
            'forks': repo.forks_count,
            'language': repo.language
        } for repo in repos]
    
    def create_repository(self, name, description=None, private=False):
        """Create a new repository"""
        user = self.client.get_user()
        repo = user.create_repo(
            name=name,
            description=description,
            private=private
        )
        return {
            'name': repo.name,
            'description': repo.description,
            'url': repo.html_url,
            'clone_url': repo.clone_url
        }
    
    @lru_cache(maxsize=100)
    def get_repository(self, owner, repo_name):
        """Get repository details"""
        try:
            repo = self.client.get_repo(f"{owner}/{repo_name}")
            return {
                'name': repo.name,
                'description': repo.description,
                'url': repo.html_url,
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'language': repo.language,
                'issues_count': repo.open_issues_count,
                'created_at': repo.created_at,
                'updated_at': repo.updated_at
            }
        except Exception:
            return None

    def _calculate_text_complexity(self, text):
        """Calculate text complexity based on length and structure"""
        if not text:
            return 1
        
        # Factors affecting complexity
        words = len(text.split())
        sentences = len(re.split(r'[.!?]+', text))
        code_blocks = len(re.findall(r'```.*?```', text, re.DOTALL))
        technical_terms = len(re.findall(r'\b(?:api|function|method|class|bug|error|exception)\b', text.lower()))
        
        # Normalize and combine factors
        complexity = (
            min(words / 100, 5) +  # Length factor
            min(sentences / 10, 2) +  # Structure factor
            min(code_blocks * 0.5, 2) +  # Technical complexity
            min(technical_terms * 0.2, 1)  # Domain complexity
        )
        
        return min(max(complexity, 1), 10)  # Ensure score is between 1-10

    def _calculate_impact_scores(self, text):
        """Calculate security, performance, and UX impact scores based on keyword analysis"""
        text_lower = text.lower()
        
        # Calculate impact scores based on keyword presence and context
        security_score = sum(2 if kw in text_lower else 0 for kw in self._security_keywords)
        performance_score = sum(2 if kw in text_lower else 0 for kw in self._performance_keywords)
        ux_score = sum(2 if kw in text_lower else 0 for kw in self._ux_keywords)
        
        # Normalize scores to 1-10 range
        return {
            'security': min(max(security_score, 1), 10),
            'performance': min(max(performance_score, 1), 10),
            'ux': min(max(ux_score, 1), 10)
        }

    def _estimate_implementation_time(self, complexity, impact_scores):
        """Estimate implementation time in hours based on complexity and impact scores"""
        base_time = complexity * 2  # Base time in hours
        impact_factor = max(impact_scores.values()) / 10  # Impact factor 0-1
        
        return round(base_time * (1 + impact_factor))

    @lru_cache(maxsize=200)
    def analyze_issue(self, owner, repo_name, issue_number):
        """Analyze a specific issue for complexity and impact"""
        try:
            repo = self.client.get_repo(f"{owner}/{repo_name}")
            issue = repo.get_issue(issue_number)
            
            # Analyze issue content
            content = f"{issue.title}\n{issue.body}"
            complexity = self._calculate_text_complexity(content)
            impact_scores = self._calculate_impact_scores(content)
            
            # Estimate implementation time
            implementation_time = self._estimate_implementation_time(complexity, impact_scores)
            
            return {
                'issue_number': issue_number,
                'title': issue.title,
                'complexity': complexity,
                'security_impact': impact_scores['security'],
                'performance_impact': impact_scores['performance'],
                'ux_impact': impact_scores['ux'],
                'implementation_time': implementation_time,
                'state': issue.state,
                'created_at': issue.created_at,
                'updated_at': issue.updated_at
            }
        except Exception as e:
            return None

    def score_issue(self, issue_analysis):
        """Calculate composite score for an issue"""
        if not issue_analysis:
            return 0
        
        # Weights for different factors
        weights = {
            'complexity': 0.25,
            'security_impact': 0.3,
            'performance_impact': 0.2,
            'ux_impact': 0.15,
            'implementation_time': 0.1
        }
        
        # Normalize implementation time to 1-10 scale
        normalized_time = min(10, max(1, 10 - (issue_analysis['implementation_time'] / 8)))
        
        # Calculate weighted score
        score = (
            weights['complexity'] * issue_analysis['complexity'] +
            weights['security_impact'] * issue_analysis['security_impact'] +
            weights['performance_impact'] * issue_analysis['performance_impact'] +
            weights['ux_impact'] * issue_analysis['ux_impact'] +
            weights['implementation_time'] * normalized_time
        )
        
        return round(score, 2)

    @lru_cache(maxsize=100)
    def analyze_issue_dependencies(self, owner, repo_name, issue_number):
        """Analyze dependencies between issues"""
        try:
            repo = self.client.get_repo(f"{owner}/{repo_name}")
            issue = repo.get_issue(issue_number)
            
            # Find referenced issues
            referenced_issues = set()
            
            # Check issue body for references
            referenced_issues.update(
                int(num) for num in re.findall(r'#(\d+)', issue.body)
            )
            
            # Check comments for references
            for comment in issue.get_comments():
                referenced_issues.update(
                    int(num) for num in re.findall(r'#(\d+)', comment.body)
                )
            
            # Get details of referenced issues
            dependencies = []
            for ref_num in referenced_issues:
                try:
                    ref_issue = repo.get_issue(ref_num)
                    dependencies.append({
                        'issue_number': ref_num,
                        'title': ref_issue.title,
                        'state': ref_issue.state,
                        'created_at': ref_issue.created_at
                    })
                except:
                    continue
            
            return {
                'issue_number': issue_number,
                'dependencies': dependencies,
                'dependency_count': len(dependencies)
            }
        except Exception:
            return None

    @lru_cache(maxsize=50)
    def prioritize_issues(self, owner, repo_name):
        """Prioritize issues based on score and dependencies"""
        try:
            repo = self.client.get_repo(f"{owner}/{repo_name}")
            issues = repo.get_issues(state='open')
            
            # Analyze all issues
            issue_analyses = {}
            dependency_map = {}
            
            for issue in issues:
                analysis = self.analyze_issue(owner, repo_name, issue.number)
                if analysis:
                    issue_analyses[issue.number] = analysis
                    deps = self.analyze_issue_dependencies(owner, repo_name, issue.number)
                    dependency_map[issue.number] = deps['dependencies'] if deps else []
            
            # Calculate scores and create dependency graph
            scores = {
                num: self.score_issue(analysis)
                for num, analysis in issue_analyses.items()
            }
            
            # Sort issues considering both score and dependencies
            prioritized_issues = []
            processed = set()
            
            def process_issue(issue_num):
                if issue_num in processed:
                    return
                
                # Process dependencies first
                for dep in dependency_map.get(issue_num, []):
                    dep_num = dep['issue_number']
                    if dep_num in issue_analyses:
                        process_issue(dep_num)
                
                processed.add(issue_num)
                prioritized_issues.append({
                    **issue_analyses[issue_num],
                    'score': scores[issue_num],
                    'dependencies': dependency_map.get(issue_num, [])
                })
            
            # Process all issues
            for issue_num in sorted(scores, key=scores.get, reverse=True):
                process_issue(issue_num)
            
            return prioritized_issues
            
        except Exception:
            return []
