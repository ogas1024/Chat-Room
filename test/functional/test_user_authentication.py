"""
用户认证功能测试
测试完整的用户注册、登录、登出流程
"""

import pytest
import time
from pathlib import Path

from test.utils.test_helpers import MockServer, MockClient, wait_for_condition
from test.fixtures.data_fixtures import UserFixtures


@pytest.mark.functional
class TestUserAuthentication:
    """用户认证功能测试"""
    
    def test_complete_registration_flow(self, mock_server):
        """测试完整注册流程"""
        # 设置服务器响应处理器
        def handle_register(message_data):
            username = message_data['data']['username']
            password = message_data['data']['password']
            
            # 模拟注册验证逻辑
            if len(username) < 3:
                return json.dumps({
                    "type": "register_response",
                    "data": {
                        "success": False,
                        "error_message": "用户名长度必须至少3个字符"
                    }
                })
            
            if len(password) < 6:
                return json.dumps({
                    "type": "register_response", 
                    "data": {
                        "success": False,
                        "error_message": "密码长度必须至少6个字符"
                    }
                })
            
            return json.dumps({
                "type": "register_response",
                "data": {
                    "success": True,
                    "user_id": 1,
                    "username": username
                }
            })
        
        mock_server.register_handler("register_request", handle_register)
        
        # 创建客户端并连接
        client = MockClient()
        assert client.connect() is True
        
        # 测试有效注册
        register_message = json.dumps({
            "type": "register_request",
            "data": {
                "username": "alice",
                "password": "password123"
            }
        })
        
        assert client.send_message(register_message) is True
        
        # 等待响应
        assert wait_for_condition(
            lambda: len(client.get_received_messages()) > 0,
            timeout=2.0
        )
        
        responses = client.get_received_messages()
        assert len(responses) > 0
        
        response_data = json.loads(responses[-1])
        assert response_data['type'] == "register_response"
        assert response_data['data']['success'] is True
        assert response_data['data']['username'] == "alice"
    
    def test_registration_validation(self, mock_server):
        """测试注册验证"""
        import json
        
        def handle_register(message_data):
            username = message_data['data']['username']
            password = message_data['data']['password']
            
            # 用户名验证
            if not username:
                error_msg = "用户名不能为空"
            elif len(username) < 3:
                error_msg = "用户名长度必须至少3个字符"
            elif len(username) > 20:
                error_msg = "用户名长度不能超过20个字符"
            # 密码验证
            elif len(password) < 6:
                error_msg = "密码长度必须至少6个字符"
            else:
                return json.dumps({
                    "type": "register_response",
                    "data": {
                        "success": True,
                        "user_id": 1,
                        "username": username
                    }
                })
            
            return json.dumps({
                "type": "register_response",
                "data": {
                    "success": False,
                    "error_message": error_msg
                }
            })
        
        mock_server.register_handler("register_request", handle_register)
        
        client = MockClient()
        client.connect()
        
        # 测试无效注册案例
        invalid_cases = [
            ("", "password123", "用户名不能为空"),
            ("ab", "password123", "用户名长度必须至少3个字符"),
            ("a" * 21, "password123", "用户名长度不能超过20个字符"),
            ("alice", "123", "密码长度必须至少6个字符"),
        ]
        
        for username, password, expected_error in invalid_cases:
            client.clear_received_messages()
            
            register_message = json.dumps({
                "type": "register_request",
                "data": {
                    "username": username,
                    "password": password
                }
            })
            
            client.send_message(register_message)
            
            # 等待响应
            wait_for_condition(
                lambda: len(client.get_received_messages()) > 0,
                timeout=2.0
            )
            
            responses = client.get_received_messages()
            assert len(responses) > 0
            
            response_data = json.loads(responses[-1])
            assert response_data['type'] == "register_response"
            assert response_data['data']['success'] is False
            assert expected_error in response_data['data']['error_message']
    
    def test_complete_login_flow(self, mock_server):
        """测试完整登录流程"""
        import json
        
        # 模拟用户数据库
        users_db = {
            "alice": {
                "user_id": 1,
                "password_hash": "hashed_password123"  # 实际应该是哈希值
            }
        }
        
        def handle_login(message_data):
            username = message_data['data']['username']
            password = message_data['data']['password']
            
            if username not in users_db:
                return json.dumps({
                    "type": "login_response",
                    "data": {
                        "success": False,
                        "error_message": "用户不存在"
                    }
                })
            
            # 简化的密码验证（实际应该验证哈希）
            if password != "password123":
                return json.dumps({
                    "type": "login_response",
                    "data": {
                        "success": False,
                        "error_message": "密码错误"
                    }
                })
            
            return json.dumps({
                "type": "login_response",
                "data": {
                    "success": True,
                    "user_id": users_db[username]["user_id"],
                    "username": username
                }
            })
        
        mock_server.register_handler("login_request", handle_login)
        
        client = MockClient()
        client.connect()
        
        # 测试成功登录
        login_message = json.dumps({
            "type": "login_request",
            "data": {
                "username": "alice",
                "password": "password123"
            }
        })
        
        client.send_message(login_message)
        
        wait_for_condition(
            lambda: len(client.get_received_messages()) > 0,
            timeout=2.0
        )
        
        responses = client.get_received_messages()
        response_data = json.loads(responses[-1])
        
        assert response_data['type'] == "login_response"
        assert response_data['data']['success'] is True
        assert response_data['data']['user_id'] == 1
        assert response_data['data']['username'] == "alice"
    
    def test_login_failure_scenarios(self, mock_server):
        """测试登录失败场景"""
        import json
        
        def handle_login(message_data):
            username = message_data['data']['username']
            password = message_data['data']['password']
            
            if username == "nonexistent":
                error_msg = "用户不存在"
            elif username == "alice" and password != "password123":
                error_msg = "密码错误"
            else:
                return json.dumps({
                    "type": "login_response",
                    "data": {
                        "success": True,
                        "user_id": 1,
                        "username": username
                    }
                })
            
            return json.dumps({
                "type": "login_response",
                "data": {
                    "success": False,
                    "error_message": error_msg
                }
            })
        
        mock_server.register_handler("login_request", handle_login)
        
        client = MockClient()
        client.connect()
        
        # 测试失败场景
        failure_cases = [
            ("nonexistent", "password123", "用户不存在"),
            ("alice", "wrongpassword", "密码错误"),
        ]
        
        for username, password, expected_error in failure_cases:
            client.clear_received_messages()
            
            login_message = json.dumps({
                "type": "login_request",
                "data": {
                    "username": username,
                    "password": password
                }
            })
            
            client.send_message(login_message)
            
            wait_for_condition(
                lambda: len(client.get_received_messages()) > 0,
                timeout=2.0
            )
            
            responses = client.get_received_messages()
            response_data = json.loads(responses[-1])
            
            assert response_data['type'] == "login_response"
            assert response_data['data']['success'] is False
            assert expected_error in response_data['data']['error_message']
    
    def test_session_management(self, mock_server):
        """测试会话管理"""
        import json
        
        active_sessions = {}
        
        def handle_login(message_data):
            username = message_data['data']['username']
            password = message_data['data']['password']
            
            if username == "alice" and password == "password123":
                session_id = f"session_{username}_{int(time.time())}"
                active_sessions[session_id] = {
                    "user_id": 1,
                    "username": username,
                    "login_time": time.time()
                }
                
                return json.dumps({
                    "type": "login_response",
                    "data": {
                        "success": True,
                        "user_id": 1,
                        "username": username,
                        "session_id": session_id
                    }
                })
            
            return json.dumps({
                "type": "login_response",
                "data": {
                    "success": False,
                    "error_message": "登录失败"
                }
            })
        
        def handle_logout(message_data):
            session_id = message_data['data'].get('session_id')
            
            if session_id in active_sessions:
                del active_sessions[session_id]
                return json.dumps({
                    "type": "logout_response",
                    "data": {
                        "success": True,
                        "message": "登出成功"
                    }
                })
            
            return json.dumps({
                "type": "logout_response",
                "data": {
                    "success": False,
                    "error_message": "无效的会话"
                }
            })
        
        mock_server.register_handler("login_request", handle_login)
        mock_server.register_handler("logout_request", handle_logout)
        
        client = MockClient()
        client.connect()
        
        # 登录
        login_message = json.dumps({
            "type": "login_request",
            "data": {
                "username": "alice",
                "password": "password123"
            }
        })
        
        client.send_message(login_message)
        wait_for_condition(lambda: len(client.get_received_messages()) > 0)
        
        login_response = json.loads(client.get_received_messages()[-1])
        assert login_response['data']['success'] is True
        session_id = login_response['data']['session_id']
        
        # 登出
        client.clear_received_messages()
        logout_message = json.dumps({
            "type": "logout_request",
            "data": {
                "session_id": session_id
            }
        })
        
        client.send_message(logout_message)
        wait_for_condition(lambda: len(client.get_received_messages()) > 0)
        
        logout_response = json.loads(client.get_received_messages()[-1])
        assert logout_response['data']['success'] is True
    
    def test_concurrent_authentication(self, mock_server):
        """测试并发认证"""
        import json
        import threading
        
        user_counter = 0
        
        def handle_register(message_data):
            nonlocal user_counter
            username = message_data['data']['username']
            
            user_counter += 1
            return json.dumps({
                "type": "register_response",
                "data": {
                    "success": True,
                    "user_id": user_counter,
                    "username": username
                }
            })
        
        mock_server.register_handler("register_request", handle_register)
        
        results = []
        
        def register_user(user_id):
            client = MockClient()
            try:
                client.connect()
                
                register_message = json.dumps({
                    "type": "register_request",
                    "data": {
                        "username": f"user_{user_id}",
                        "password": "password123"
                    }
                })
                
                client.send_message(register_message)
                
                # 等待响应
                if wait_for_condition(lambda: len(client.get_received_messages()) > 0):
                    response = json.loads(client.get_received_messages()[-1])
                    if response['data']['success']:
                        results.append(f"user_{user_id}_success")
                    else:
                        results.append(f"user_{user_id}_failed")
                else:
                    results.append(f"user_{user_id}_timeout")
                    
            except Exception as e:
                results.append(f"user_{user_id}_exception")
            finally:
                client.disconnect()
        
        # 创建多个线程同时注册
        threads = []
        for i in range(5):
            thread = threading.Thread(target=register_user, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        assert len(results) == 5
        success_count = len([r for r in results if "success" in r])
        assert success_count == 5  # 所有注册都应该成功
    
    def test_authentication_with_chinese_users(self, mock_server):
        """测试中文用户认证"""
        import json
        
        def handle_register(message_data):
            username = message_data['data']['username']
            return json.dumps({
                "type": "register_response",
                "data": {
                    "success": True,
                    "user_id": 1,
                    "username": username
                }
            }, ensure_ascii=False)
        
        def handle_login(message_data):
            username = message_data['data']['username']
            return json.dumps({
                "type": "login_response",
                "data": {
                    "success": True,
                    "user_id": 1,
                    "username": username
                }
            }, ensure_ascii=False)
        
        mock_server.register_handler("register_request", handle_register)
        mock_server.register_handler("login_request", handle_login)
        
        client = MockClient()
        client.connect()
        
        # 注册中文用户
        register_message = json.dumps({
            "type": "register_request",
            "data": {
                "username": "测试用户",
                "password": "中文密码123"
            }
        }, ensure_ascii=False)
        
        client.send_message(register_message)
        wait_for_condition(lambda: len(client.get_received_messages()) > 0)
        
        register_response = json.loads(client.get_received_messages()[-1])
        assert register_response['data']['success'] is True
        assert register_response['data']['username'] == "测试用户"
        
        # 登录中文用户
        client.clear_received_messages()
        login_message = json.dumps({
            "type": "login_request",
            "data": {
                "username": "测试用户",
                "password": "中文密码123"
            }
        }, ensure_ascii=False)
        
        client.send_message(login_message)
        wait_for_condition(lambda: len(client.get_received_messages()) > 0)
        
        login_response = json.loads(client.get_received_messages()[-1])
        assert login_response['data']['success'] is True
        assert login_response['data']['username'] == "测试用户"
