
import os


class ExerciseLoader:
    
    def load_exercise(self, exercise_code, bucket="default"):

        raise NotImplementedError("Subclasses must implement load_exercise()")


class FileSystemLoader(ExerciseLoader):
    
    def __init__(self, plugin_dir):
  
        self.plugin_dir = plugin_dir
    
    def load_exercise(self, exercise_code, bucket="default"):

        exercise_dir = os.path.join(self.plugin_dir, 'bucket', bucket, exercise_code)
        index_file = os.path.join(exercise_dir, 'index.md')
        
        if not os.path.exists(exercise_dir):
            raise FileNotFoundError(f"Exercise directory not found: {exercise_dir}")
        
        if not os.path.exists(index_file):
            raise FileNotFoundError(f"Exercise index.md not found: {index_file}")
        
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content, exercise_dir




class APILoader(ExerciseLoader):
    """Load exercises from remote API (future implementation)"""
    
    def __init__(self, api_url, api_key=None):
        """
        Initialize API loader
        
        Args:
            api_url: Base URL of the API (e.g., "https://exercises.example.com/api")
            api_key: Optional API key for authentication
        """
        self.api_url = api_url
        self.api_key = api_key
    
    def load_exercise(self, exercise_code, bucket="default"):
        """
        Load exercise from API
        
        Returns:
            tuple: (markdown_content, None)
                   exercise_dir is None because files are not local
        """
        # Future implementation:
        # import requests
        # 
        # headers = {}
        # if self.api_key:
        #     headers['Authorization'] = f'Bearer {self.api_key}'
        # 
        # response = requests.get(
        #     f"{self.api_url}/exercises/{bucket}/{exercise_code}",
        #     headers=headers
        # )
        # 
        # if response.status_code == 404:
        #     raise FileNotFoundError(f"Exercise not found: {bucket}/{exercise_code}")
        # 
        # response.raise_for_status()
        # data = response.json()
        # 
        # return data['markdown'], None
        
        raise NotImplementedError("API loader not yet implemented")



def create_loader(loader_type="filesystem", **kwargs):
    """
    Factory function to create an exercise loader
    
    Args:
        loader_type: Type of loader ("filesystem" or "api")
        **kwargs: Additional arguments passed to the loader
    
    Returns:
        ExerciseLoader instance
    
    Example:
        loader = create_loader("filesystem", plugin_dir="/path/to/plugin")
        loader = create_loader("api", api_url="https://...", api_key="...")
    """
    loaders = {
        "filesystem": FileSystemLoader,
        "api": APILoader,
    }
    
    if loader_type not in loaders:
        raise ValueError(f"Unknown loader type: {loader_type}")
    
    return loaders[loader_type](**kwargs)
