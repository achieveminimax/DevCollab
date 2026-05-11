#!/usr/bin/env python3
"""
沙箱执行器

负责具体的代码执行任务，与沙箱管理器配合使用。
提供更高级的代码执行功能，如测试执行、代码分析等。
"""

import os
import json
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
from .manager import SandboxManager


class CodeExecutor:
    """代码执行器类"""
    
    def __init__(self, sandbox_manager: Optional[SandboxManager] = None):
        """
        初始化代码执行器
        
        Args:
            sandbox_manager: 沙箱管理器实例，如果为None则创建新的
        """
        self.sandbox_manager = sandbox_manager or SandboxManager()
        self.execution_history = []
    
    def execute_python_code(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        执行Python代码
        
        Args:
            code: Python代码字符串
            timeout: 执行超时时间（秒）
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        start_time = time.time()
        
        try:
            # 使用沙箱管理器执行代码
            result = self.sandbox_manager.execute_code(code, "python")
            
            # 记录执行历史
            execution_record = {
                "timestamp": time.time(),
                "language": "python",
                "code_length": len(code),
                "success": result["success"],
                "execution_time": result["execution_time"],
                "has_output": bool(result["output"]),
                "has_error": bool(result["error"])
            }
            self.execution_history.append(execution_record)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"执行器错误: {str(e)}",
                "execution_time": time.time() - start_time,
                "return_code": -1
            }
    
    def execute_javascript_code(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        执行JavaScript代码
        
        Args:
            code: JavaScript代码字符串
            timeout: 执行超时时间（秒）
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        start_time = time.time()
        
        try:
            # 使用沙箱管理器执行代码
            result = self.sandbox_manager.execute_code(code, "javascript")
            
            # 记录执行历史
            execution_record = {
                "timestamp": time.time(),
                "language": "javascript",
                "code_length": len(code),
                "success": result["success"],
                "execution_time": result["execution_time"],
                "has_output": bool(result["output"]),
                "has_error": bool(result["error"])
            }
            self.execution_history.append(execution_record)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"执行器错误: {str(e)}",
                "execution_time": time.time() - start_time,
                "return_code": -1
            }
    
    def execute_typescript_code(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        执行TypeScript代码
        
        Args:
            code: TypeScript代码字符串
            timeout: 执行超时时间（秒）
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        start_time = time.time()
        
        try:
            # 使用沙箱管理器执行代码
            result = self.sandbox_manager.execute_code(code, "typescript")
            
            # 记录执行历史
            execution_record = {
                "timestamp": time.time(),
                "language": "typescript",
                "code_length": len(code),
                "success": result["success"],
                "execution_time": result["execution_time"],
                "has_output": bool(result["output"]),
                "has_error": bool(result["error"])
            }
            self.execution_history.append(execution_record)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"执行器错误: {str(e)}",
                "execution_time": time.time() - start_time,
                "return_code": -1
            }
    
    def run_tests(self, test_code: str, language: str = "python") -> Dict[str, Any]:
        """
        运行测试代码
        
        Args:
            test_code: 测试代码
            language: 编程语言
            
        Returns:
            Dict[str, Any]: 测试结果
        """
        if language == "python":
            return self._run_python_tests(test_code)
        elif language == "javascript":
            return self._run_javascript_tests(test_code)
        elif language == "typescript":
            return self._run_typescript_tests(test_code)
        else:
            return {
                "success": False,
                "output": "",
                "error": f"不支持的语言: {language}",
                "execution_time": 0,
                "test_results": []
            }
    
    def _run_python_tests(self, test_code: str) -> Dict[str, Any]:
        """运行Python测试"""
        # 创建测试文件
        test_file_content = f'''
import sys
import json

{test_code}

if __name__ == "__main__":
    results = []
    
    # 收集测试结果
    test_functions = [func for func in dir() if func.startswith('test_')]
    
    for test_func_name in test_functions:
        test_func = globals()[test_func_name]
        try:
            test_func()
            results.append({{
                "name": test_func_name,
                "status": "passed",
                "error": None
            }})
        except AssertionError as e:
            results.append({{
                "name": test_func_name,
                "status": "failed",
                "error": str(e)
            }})
        except Exception as e:
            results.append({{
                "name": test_func_name,
                "status": "error",
                "error": str(e)
            }})
    
    # 输出测试结果
    print(json.dumps({{
        "total": len(results),
        "passed": len([r for r in results if r["status"] == "passed"]),
        "failed": len([r for r in results if r["status"] == "failed"]),
        "errors": len([r for r in results if r["status"] == "error"]),
        "results": results
    }}, indent=2))
'''
        
        result = self.execute_python_code(test_file_content)
        
        if result["success"]:
            try:
                # 解析测试结果
                output_lines = result["output"].strip().split('\n')
                json_output = None
                
                for line in output_lines:
                    if line.strip().startswith('{'):
                        json_output = json.loads(line.strip())
                        break
                
                if json_output:
                    result["test_results"] = json_output
                else:
                    result["test_results"] = {
                        "total": 0,
                        "passed": 0,
                        "failed": 0,
                        "errors": 0,
                        "results": []
                    }
            except json.JSONDecodeError:
                result["test_results"] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "errors": 0,
                    "results": []
                }
        
        return result
    
    def _run_javascript_tests(self, test_code: str) -> Dict[str, Any]:
        """运行JavaScript测试"""
        # 创建测试文件
        test_file_content = f'''
const testResults = [];

{test_code}

// 运行测试
const testFunctions = Object.keys(global).filter(key => key.startsWith('test_'));
let passed = 0;
let failed = 0;
let errors = 0;

testFunctions.forEach(testName => {{
    try {{
        global[testName]();
        testResults.push({{
            name: testName,
            status: 'passed',
            error: null
        }});
        passed++;
    }} catch (error) {{
        if (error.name === 'AssertionError') {{
            testResults.push({{
                name: testName,
                status: 'failed',
                error: error.message
            }});
            failed++;
        }} else {{
            testResults.push({{
                name: testName,
                status: 'error',
                error: error.message
            }});
            errors++;
        }}
    }}
}});

console.log(JSON.stringify({{
    total: testFunctions.length,
    passed,
    failed,
    errors,
    results: testResults
}}, null, 2));
'''
        
        result = self.execute_javascript_code(test_file_content)
        
        if result["success"]:
            try:
                output_lines = result["output"].strip().split('\n')
                json_output = None
                
                for line in output_lines:
                    if line.strip().startswith('{'):
                        json_output = json.loads(line.strip())
                        break
                
                if json_output:
                    result["test_results"] = json_output
                else:
                    result["test_results"] = {
                        "total": 0,
                        "passed": 0,
                        "failed": 0,
                        "errors": 0,
                        "results": []
                    }
            except json.JSONDecodeError:
                result["test_results"] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "errors": 0,
                    "results": []
                }
        
        return result
    
    def _run_typescript_tests(self, test_code: str) -> Dict[str, Any]:
        """运行TypeScript测试"""
        # TypeScript测试需要更复杂的设置，这里简化处理
        return self._run_javascript_tests(test_code)
    
    def analyze_code_quality(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        分析代码质量
        
        Args:
            code: 代码字符串
            language: 编程语言
            
        Returns:
            Dict[str, Any]: 代码质量分析结果
        """
        analysis_result = {
            "language": language,
            "code_length": len(code),
            "lines_of_code": len(code.split('\n')),
            "analysis_time": time.time(),
            "metrics": {},
            "issues": []
        }
        
        # 基础代码分析
        if language == "python":
            analysis_result["metrics"] = self._analyze_python_code(code)
        elif language == "javascript":
            analysis_result["metrics"] = self._analyze_javascript_code(code)
        elif language == "typescript":
            analysis_result["metrics"] = self._analyze_typescript_code(code)
        
        return analysis_result
    
    def _analyze_python_code(self, code: str) -> Dict[str, Any]:
        """分析Python代码"""
        lines = code.split('\n')
        
        metrics = {
            "line_count": len(lines),
            "function_count": sum(1 for line in lines if line.strip().startswith('def ')),
            "class_count": sum(1 for line in lines if line.strip().startswith('class ')),
            "import_count": sum(1 for line in lines if line.strip().startswith('import ') or line.strip().startswith('from ')),
            "comment_lines": sum(1 for line in lines if line.strip().startswith('#')),
            "empty_lines": sum(1 for line in lines if line.strip() == ''),
            "avg_line_length": sum(len(line) for line in lines) / max(len(lines), 1)
        }
        
        # 计算代码密度（非空非注释行比例）
        code_lines = len(lines) - metrics["comment_lines"] - metrics["empty_lines"]
        metrics["code_density"] = code_lines / max(len(lines), 1)
        
        return metrics
    
    def _analyze_javascript_code(self, code: str) -> Dict[str, Any]:
        """分析JavaScript代码"""
        lines = code.split('\n')
        
        metrics = {
            "line_count": len(lines),
            "function_count": sum(1 for line in lines if 'function ' in line or '=>' in line),
            "class_count": sum(1 for line in lines if line.strip().startswith('class ')),
            "import_count": sum(1 for line in lines if line.strip().startswith('import ') or line.strip().startswith('require(')),
            "comment_lines": sum(1 for line in lines if line.strip().startswith('//') or line.strip().startswith('/*')),
            "empty_lines": sum(1 for line in lines if line.strip() == ''),
            "avg_line_length": sum(len(line) for line in lines) / max(len(lines), 1)
        }
        
        code_lines = len(lines) - metrics["comment_lines"] - metrics["empty_lines"]
        metrics["code_density"] = code_lines / max(len(lines), 1)
        
        return metrics
    
    def _analyze_typescript_code(self, code: str) -> Dict[str, Any]:
        """分析TypeScript代码"""
        # TypeScript分析类似JavaScript，但增加类型相关统计
        js_metrics = self._analyze_javascript_code(code)
        
        lines = code.split('\n')
        js_metrics["type_annotations"] = sum(1 for line in lines if ':' in line and ('string' in line or 'number' in line or 'boolean' in line or 'any' in line))
        js_metrics["interface_count"] = sum(1 for line in lines if line.strip().startswith('interface ') or line.strip().startswith('type '))
        
        return js_metrics
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取执行历史
        
        Args:
            limit: 返回的历史记录数量限制
            
        Returns:
            List[Dict[str, Any]]: 执行历史记录
        """
        return self.execution_history[-limit:] if self.execution_history else []
    
    def clear_history(self):
        """清空执行历史"""
        self.execution_history.clear()


if __name__ == "__main__":
    # 测试代码执行器
    executor = CodeExecutor()
    
    # 测试Python代码执行
    python_code = '''
def add(a, b):
    return a + b

result = add(3, 4)
print(f"3 + 4 = {result}")
'''
    
    print("执行Python代码...")
    result = executor.execute_python_code(python_code)
    print("执行结果:", json.dumps(result, indent=2, ensure_ascii=False))
    
    # 测试代码质量分析
    print("\n分析Python代码质量...")
    analysis = executor.analyze_code_quality(python_code, "python")
    print("分析结果:", json.dumps(analysis, indent=2, ensure_ascii=False))
    
    # 测试测试执行
    test_code = '''
def test_addition():
    assert 1 + 1 == 2
    
def test_subtraction():
    assert 5 - 3 == 2
    
def test_failure():
    assert 2 * 2 == 5  # 这个测试会失败
'''
    
    print("\n运行Python测试...")
    test_result = executor.run_tests(test_code, "python")
    print("测试结果:", json.dumps(test_result.get("test_results", {}), indent=2, ensure_ascii=False))
    
    # 显示执行历史
    print("\n执行历史:")
    history = executor.get_execution_history()
    for record in history:
        print(f"  - {record}")