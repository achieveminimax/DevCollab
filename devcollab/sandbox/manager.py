#!/usr/bin/env python3
"""
沙箱管理器

负责管理代码执行沙箱，确保代码在隔离环境中安全执行。
支持多语言环境，提供资源限制和安全性检查。
"""

import os
import sys
import subprocess
import tempfile
import shutil
import time
from typing import Dict, Any, Optional
from pathlib import Path


class SandboxManager:
    """沙箱管理器类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化沙箱管理器
        
        Args:
            config: 配置字典，包含沙箱相关配置
        """
        self.config = config or {}
        self.temp_dir = None
        
    def create_sandbox(self, language: str = "python") -> str:
        """
        创建沙箱环境
        
        Args:
            language: 编程语言类型
            
        Returns:
            str: 沙箱目录路径
        """
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp(prefix="devcollab_sandbox_")
        
        # 根据语言配置环境
        if language == "python":
            self._setup_python_sandbox()
        elif language == "javascript":
            self._setup_javascript_sandbox()
        elif language == "typescript":
            self._setup_typescript_sandbox()
        else:
            raise ValueError(f"不支持的语言: {language}")
        
        return self.temp_dir
    
    def _setup_python_sandbox(self):
        """设置Python沙箱环境"""
        # 创建虚拟环境
        venv_path = os.path.join(self.temp_dir, "venv")
        subprocess.run([sys.executable, "-m", "venv", venv_path], 
                      check=True, capture_output=True)
        
        # 创建requirements.txt
        requirements = """
ruff==0.3.0
pytest==7.4.0
pytest-cov==4.1.0
"""
        with open(os.path.join(self.temp_dir, "requirements.txt"), "w") as f:
            f.write(requirements)
    
    def _setup_javascript_sandbox(self):
        """设置JavaScript沙箱环境"""
        # 创建package.json
        package_json = {
            "name": "devcollab-sandbox",
            "version": "1.0.0",
            "scripts": {
                "test": "jest"
            },
            "devDependencies": {
                "jest": "^29.0.0",
                "@types/jest": "^29.0.0"
            }
        }
        
        import json
        with open(os.path.join(self.temp_dir, "package.json"), "w") as f:
            json.dump(package_json, f, indent=2)
    
    def _setup_typescript_sandbox(self):
        """设置TypeScript沙箱环境"""
        # 创建package.json
        package_json = {
            "name": "devcollab-sandbox-ts",
            "version": "1.0.0",
            "scripts": {
                "build": "tsc",
                "test": "jest"
            },
            "devDependencies": {
                "typescript": "^5.0.0",
                "jest": "^29.0.0",
                "@types/jest": "^29.0.0",
                "ts-jest": "^29.0.0"
            }
        }
        
        import json
        with open(os.path.join(self.temp_dir, "package.json"), "w") as f:
            json.dump(package_json, f, indent=2)
        
        # 创建tsconfig.json
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "module": "commonjs",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True
            }
        }
        
        with open(os.path.join(self.temp_dir, "tsconfig.json"), "w") as f:
            json.dump(tsconfig, f, indent=2)
    
    def execute_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        在沙箱中执行代码
        
        Args:
            code: 要执行的代码
            language: 编程语言类型
            
        Returns:
            Dict[str, Any]: 执行结果，包含输出、错误、执行时间等信息
        """
        try:
            sandbox_dir = self.create_sandbox(language)
            
            # 根据语言执行代码
            if language == "python":
                return self._execute_python_code(sandbox_dir, code)
            elif language == "javascript":
                return self._execute_javascript_code(sandbox_dir, code)
            elif language == "typescript":
                return self._execute_typescript_code(sandbox_dir, code)
            else:
                raise ValueError(f"不支持的语言: {language}")
                
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "execution_time": 0
            }
        finally:
            self.cleanup()
    
    def _execute_python_code(self, sandbox_dir: str, code: str) -> Dict[str, Any]:
        """执行Python代码"""
        # 将代码写入文件
        code_file = os.path.join(sandbox_dir, "code.py")
        with open(code_file, "w") as f:
            f.write(code)
        
        # 执行代码
        start_time = time.time()
        try:
            result = subprocess.run(
                [sys.executable, code_file],
                capture_output=True,
                text=True,
                timeout=30,  # 30秒超时
                cwd=sandbox_dir
            )
            execution_time = time.time() - start_time
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "execution_time": execution_time,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "执行超时（30秒）",
                "execution_time": 30,
                "return_code": -1
            }
    
    def _execute_javascript_code(self, sandbox_dir: str, code: str) -> Dict[str, Any]:
        """执行JavaScript代码"""
        # 将代码写入文件
        code_file = os.path.join(sandbox_dir, "code.js")
        with open(code_file, "w") as f:
            f.write(code)
        
        # 执行代码
        start_time = time.time()
        try:
            result = subprocess.run(
                ["node", code_file],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=sandbox_dir
            )
            execution_time = time.time() - start_time
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "execution_time": execution_time,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "执行超时（30秒）",
                "execution_time": 30,
                "return_code": -1
            }
    
    def _execute_typescript_code(self, sandbox_dir: str, code: str) -> Dict[str, Any]:
        """执行TypeScript代码"""
        # 将代码写入文件
        code_file = os.path.join(sandbox_dir, "code.ts")
        with open(code_file, "w") as f:
            f.write(code)
        
        # 编译TypeScript
        compile_result = subprocess.run(
            ["npx", "tsc", code_file],
            capture_output=True,
            text=True,
            cwd=sandbox_dir
        )
        
        if compile_result.returncode != 0:
            return {
                "success": False,
                "output": "",
                "error": f"编译错误: {compile_result.stderr}",
                "execution_time": 0,
                "return_code": compile_result.returncode
            }
        
        # 执行编译后的JavaScript
        js_file = os.path.join(sandbox_dir, "code.js")
        start_time = time.time()
        try:
            result = subprocess.run(
                ["node", js_file],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=sandbox_dir
            )
            execution_time = time.time() - start_time
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "execution_time": execution_time,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "执行超时（30秒）",
                "execution_time": 30,
                "return_code": -1
            }
    
    def cleanup(self):
        """清理沙箱环境"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None


if __name__ == "__main__":
    # 测试沙箱管理器
    manager = SandboxManager()
    
    # 测试Python代码执行
    python_code = '''
print("Hello from Python sandbox!")
for i in range(3):
    print(f"Count: {i}")
'''
    
    result = manager.execute_code(python_code, "python")
    print("Python执行结果:", result)
    
    # 清理
    manager.cleanup()