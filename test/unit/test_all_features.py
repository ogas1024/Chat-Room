#!/usr/bin/env python3
"""
Chat-Room 全功能测试脚本
测试所有已实现的功能模块
"""

import os
import sys
import time
import tempfile
import threading

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from server.core.server import ChatRoomServer
from client.network.client import ChatClient
from shared.constants import DEFAULT_HOST, DEFAULT_PORT


class FeatureTester:
    """功能测试器"""
    
    def __init__(self):
        self.server = None
        self.server_thread = None
        self.test_port = DEFAULT_PORT + 1000  # 使用不同端口避免冲突
        self.clients = []
        
    def setup_test_environment(self):
        """设置测试环境"""
        print("🔧 设置测试环境...")
        
        # 启动测试服务器
        self.server = ChatRoomServer(DEFAULT_HOST, self.test_port)
        self.server_thread = threading.Thread(target=self.server.start, daemon=True)
        self.server_thread.start()
        
        # 等待服务器启动
        time.sleep(2)
        print(f"✅ 测试服务器已启动 ({DEFAULT_HOST}:{self.test_port})")
        
    def cleanup_test_environment(self):
        """清理测试环境"""
        print("🧹 清理测试环境...")
        
        # 断开所有客户端
        for client in self.clients:
            try:
                client.disconnect()
            except:
                pass
        
        # 停止服务器
        if self.server:
            try:
                self.server.stop()
            except:
                pass
        
        print("✅ 测试环境已清理")
    
    def test_basic_connection(self):
        """测试基本连接功能"""
        print("\n🧪 测试基本连接功能...")
        
        try:
            client = ChatClient(DEFAULT_HOST, self.test_port)
            self.clients.append(client)
            
            # 测试连接
            if client.connect():
                print("✅ 客户端连接成功")
                
                # 测试断开
                client.disconnect()
                print("✅ 客户端断开成功")
                return True
            else:
                print("❌ 客户端连接失败")
                return False
                
        except Exception as e:
            print(f"❌ 连接测试异常: {e}")
            return False
    
    def test_user_authentication(self):
        """测试用户认证功能"""
        print("\n🧪 测试用户认证功能...")
        
        try:
            client = ChatClient(DEFAULT_HOST, self.test_port)
            self.clients.append(client)
            
            if not client.connect():
                print("❌ 无法连接到服务器")
                return False
            
            # 测试注册
            success, message = client.register("testuser", "testpass")
            if success:
                print("✅ 用户注册成功")
            else:
                print(f"⚠️  注册失败: {message}")
            
            # 测试登录
            success, message = client.login("testuser", "testpass")
            if success:
                print("✅ 用户登录成功")
                
                # 测试用户信息获取
                success, message, user_info = client.get_user_info()
                if success:
                    print(f"✅ 用户信息获取成功: {user_info['username']}")
                else:
                    print(f"❌ 用户信息获取失败: {message}")
                
                return True
            else:
                print(f"❌ 登录失败: {message}")
                return False
                
        except Exception as e:
            print(f"❌ 认证测试异常: {e}")
            return False
    
    def test_chat_functionality(self):
        """测试聊天功能"""
        print("\n🧪 测试聊天功能...")
        
        try:
            # 创建两个客户端
            client1 = ChatClient(DEFAULT_HOST, self.test_port)
            client2 = ChatClient(DEFAULT_HOST, self.test_port)
            self.clients.extend([client1, client2])
            
            # 连接和登录
            if not (client1.connect() and client2.connect()):
                print("❌ 客户端连接失败")
                return False
            
            # 注册和登录用户
            client1.register("user1", "pass1")
            client2.register("user2", "pass2")
            
            success1, _ = client1.login("user1", "pass1")
            success2, _ = client2.login("user2", "pass2")
            
            if not (success1 and success2):
                print("❌ 用户登录失败")
                return False
            
            print("✅ 两个用户登录成功")
            
            # 测试聊天组功能
            success, message = client1.create_chat_group("testgroup", ["user2"])
            if success:
                print("✅ 聊天组创建成功")
            else:
                print(f"⚠️  聊天组创建失败: {message}")
            
            # 进入聊天组
            success1, _ = client1.enter_chat_group("testgroup")
            success2, _ = client2.enter_chat_group("testgroup")
            
            if success1 and success2:
                print("✅ 用户进入聊天组成功")
                
                # 测试消息发送
                group_id = client1.current_chat_group['id']
                success = client1.send_chat_message("Hello from user1!", group_id)
                if success:
                    print("✅ 消息发送成功")
                    time.sleep(0.5)  # 等待消息传播
                    return True
                else:
                    print("❌ 消息发送失败")
                    return False
            else:
                print("❌ 进入聊天组失败")
                return False
                
        except Exception as e:
            print(f"❌ 聊天功能测试异常: {e}")
            return False
    
    def test_file_transfer(self):
        """测试文件传输功能"""
        print("\n🧪 测试文件传输功能...")
        
        try:
            client = ChatClient(DEFAULT_HOST, self.test_port)
            self.clients.append(client)
            
            if not client.connect():
                print("❌ 无法连接到服务器")
                return False
            
            # 登录
            client.register("fileuser", "filepass")
            success, _ = client.login("fileuser", "filepass")
            if not success:
                print("❌ 登录失败")
                return False
            
            # 进入公频聊天组
            success, _ = client.enter_chat_group("public")
            if not success:
                print("❌ 进入聊天组失败")
                return False
            
            # 创建测试文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("这是一个测试文件内容")
                test_file_path = f.name
            
            try:
                # 测试文件上传
                success, message = client.send_file(test_file_path)
                if success:
                    print("✅ 文件上传成功")
                    
                    # 测试文件列表
                    success, message, files = client.list_files()
                    if success and files:
                        print(f"✅ 文件列表获取成功，共 {len(files)} 个文件")
                        
                        # 测试文件下载
                        file_id = files[0]['file_id']
                        success, message = client.download_file(file_id)
                        if success:
                            print("✅ 文件下载成功")
                            return True
                        else:
                            print(f"❌ 文件下载失败: {message}")
                    else:
                        print("❌ 文件列表获取失败")
                else:
                    print(f"❌ 文件上传失败: {message}")
                    
            finally:
                # 清理测试文件
                try:
                    os.unlink(test_file_path)
                except:
                    pass
            
            return False
            
        except Exception as e:
            print(f"❌ 文件传输测试异常: {e}")
            return False
    
    def test_ai_integration(self):
        """测试AI集成功能"""
        print("\n🧪 测试AI集成功能...")
        
        try:
            client = ChatClient(DEFAULT_HOST, self.test_port)
            self.clients.append(client)
            
            if not client.connect():
                print("❌ 无法连接到服务器")
                return False
            
            # 登录
            client.register("aiuser", "aipass")
            success, _ = client.login("aiuser", "aipass")
            if not success:
                print("❌ 登录失败")
                return False
            
            # 测试AI状态查询
            success, response = client.send_ai_request("status")
            if success:
                print("✅ AI状态查询成功")
                print(f"   响应: {response[:100]}...")
                
                # 测试AI帮助
                success, response = client.send_ai_request("help")
                if success:
                    print("✅ AI帮助查询成功")
                    return True
                else:
                    print(f"❌ AI帮助查询失败: {response}")
            else:
                print(f"❌ AI状态查询失败: {response}")
            
            return False
            
        except Exception as e:
            print(f"❌ AI集成测试异常: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 Chat-Room 全功能测试开始")
        print("=" * 60)
        
        # 设置测试环境
        self.setup_test_environment()
        
        # 定义测试用例
        tests = [
            ("基本连接功能", self.test_basic_connection),
            ("用户认证功能", self.test_user_authentication),
            ("聊天功能", self.test_chat_functionality),
            ("文件传输功能", self.test_file_transfer),
            ("AI集成功能", self.test_ai_integration),
        ]
        
        # 运行测试
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} 测试通过")
                else:
                    print(f"❌ {test_name} 测试失败")
            except Exception as e:
                print(f"❌ {test_name} 测试异常: {e}")
        
        # 清理环境
        self.cleanup_test_environment()
        
        # 测试结果
        print(f"\n{'='*60}")
        print(f"测试结果: {passed}/{total} 通过")
        
        if passed == total:
            print("🎉 所有功能测试通过！Chat-Room系统运行正常！")
        elif passed > 0:
            print("⚠️  部分功能测试通过，请检查失败的测试项")
        else:
            print("❌ 所有功能测试失败，请检查系统配置")
        
        return passed == total


def main():
    """主函数"""
    tester = FeatureTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
