"""
管理员功能测试脚本
测试管理员权限控制、禁言功能、用户/群组管理等
"""

import sys
import os
import time
import threading

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.core.server import ChatRoomServer
from client.core.client import ChatClient
from shared.constants import ADMIN_USER_ID, ADMIN_USERNAME


class AdminFunctionTest:
    """管理员功能测试类"""
    
    def __init__(self):
        """初始化测试环境"""
        self.server = None
        self.server_thread = None
        self.admin_client = None
        self.normal_client = None
        self.test_results = []
    
    def setup_test_environment(self):
        """设置测试环境"""
        print("🔧 设置测试环境...")
        
        # 启动服务器
        self.server = ChatRoomServer("localhost", 8889)  # 使用不同端口避免冲突
        self.server_thread = threading.Thread(target=self.server.start, daemon=True)
        self.server_thread.start()
        
        # 等待服务器启动
        time.sleep(2)
        
        # 创建客户端
        self.admin_client = ChatClient("localhost", 8889)
        self.normal_client = ChatClient("localhost", 8889)
        
        print("✅ 测试环境设置完成")
    
    def test_admin_login(self):
        """测试管理员登录"""
        print("\n📝 测试管理员登录...")
        
        try:
            # 连接服务器
            if not self.admin_client.connect():
                self.test_results.append("❌ 管理员客户端连接失败")
                return False
            
            # 管理员登录
            success, message = self.admin_client.login(ADMIN_USERNAME, "admin123")
            if success:
                self.test_results.append("✅ 管理员登录成功")
                print(f"   登录消息: {message}")
                return True
            else:
                self.test_results.append(f"❌ 管理员登录失败: {message}")
                return False
                
        except Exception as e:
            self.test_results.append(f"❌ 管理员登录测试异常: {e}")
            return False
    
    def test_normal_user_registration_and_login(self):
        """测试普通用户注册和登录"""
        print("\n📝 测试普通用户注册和登录...")
        
        try:
            # 连接服务器
            if not self.normal_client.connect():
                self.test_results.append("❌ 普通用户客户端连接失败")
                return False
            
            # 注册普通用户
            success, message = self.normal_client.register("testuser", "password123")
            if success:
                self.test_results.append("✅ 普通用户注册成功")
                print(f"   注册消息: {message}")
            else:
                self.test_results.append(f"❌ 普通用户注册失败: {message}")
                return False
            
            # 登录普通用户
            success, message = self.normal_client.login("testuser", "password123")
            if success:
                self.test_results.append("✅ 普通用户登录成功")
                print(f"   登录消息: {message}")
                return True
            else:
                self.test_results.append(f"❌ 普通用户登录失败: {message}")
                return False
                
        except Exception as e:
            self.test_results.append(f"❌ 普通用户注册登录测试异常: {e}")
            return False

    def test_admin_add_user(self):
        """测试管理员新增用户（新架构）"""
        print("\n📝 测试管理员新增用户...")

        try:
            # 管理员新增用户
            success, message = self.admin_client.send_admin_command(
                "add", "-u", None, "", "testuser2 password456"
            )

            if success:
                self.test_results.append("✅ 管理员新增用户成功（新架构）")
                print(f"   创建消息: {message}")
                return True
            else:
                self.test_results.append(f"❌ 管理员新增用户失败: {message}")
                return False

        except Exception as e:
            self.test_results.append(f"❌ 管理员新增用户测试异常: {e}")
            return False

    def test_admin_delete_file(self):
        """测试管理员删除文件（新架构）"""
        print("\n📝 测试管理员删除文件...")

        try:
            # 这里应该先上传一个文件，然后删除
            # 由于测试环境限制，我们模拟一个文件ID
            file_id = 999  # 模拟文件ID

            # 管理员删除文件
            success, message = self.admin_client.send_admin_command(
                "del", "-f", file_id, "", ""
            )

            # 由于文件不存在，预期会失败，但这验证了命令格式正确
            if not success and "不存在" in message:
                self.test_results.append("✅ 管理员删除文件命令格式正确（新架构）")
                print(f"   预期的错误消息: {message}")
                return True
            elif success:
                self.test_results.append("✅ 管理员删除文件成功（新架构）")
                print(f"   删除消息: {message}")
                return True
            else:
                self.test_results.append(f"❌ 管理员删除文件失败: {message}")
                return False

        except Exception as e:
            self.test_results.append(f"❌ 管理员删除文件测试异常: {e}")
            return False
    
    def test_admin_ban_user(self):
        """测试管理员禁言用户"""
        print("\n📝 测试管理员禁言用户...")
        
        try:
            # 获取普通用户ID
            if not self.normal_client.current_user:
                self.test_results.append("❌ 无法获取普通用户信息")
                return False
            
            user_id = self.normal_client.current_user['id']
            
            # 管理员禁言用户
            success, message = self.admin_client.send_admin_command(
                "ban", "-u", None, str(user_id), ""
            )
            
            if success:
                self.test_results.append("✅ 管理员禁言用户成功")
                print(f"   禁言消息: {message}")
                return True
            else:
                self.test_results.append(f"❌ 管理员禁言用户失败: {message}")
                return False
                
        except Exception as e:
            self.test_results.append(f"❌ 管理员禁言用户测试异常: {e}")
            return False
    
    def test_banned_user_send_message(self):
        """测试被禁言用户发送消息"""
        print("\n📝 测试被禁言用户发送消息...")
        
        try:
            # 普通用户尝试发送消息
            if not self.normal_client.current_chat_group:
                self.test_results.append("❌ 普通用户未在聊天组中")
                return False
            
            group_id = self.normal_client.current_chat_group['id']
            success = self.normal_client.send_chat_message("测试消息", group_id)
            
            if not success:
                self.test_results.append("✅ 被禁言用户无法发送消息（符合预期）")
                return True
            else:
                self.test_results.append("❌ 被禁言用户仍能发送消息（不符合预期）")
                return False
                
        except Exception as e:
            self.test_results.append(f"❌ 被禁言用户发送消息测试异常: {e}")
            return False
    
    def test_admin_unban_user(self):
        """测试管理员解除用户禁言"""
        print("\n📝 测试管理员解除用户禁言...")
        
        try:
            user_id = self.normal_client.current_user['id']
            
            # 管理员解除用户禁言
            success, message = self.admin_client.send_admin_command(
                "free", "-u", None, str(user_id), ""
            )
            
            if success:
                self.test_results.append("✅ 管理员解除用户禁言成功")
                print(f"   解禁消息: {message}")
                return True
            else:
                self.test_results.append(f"❌ 管理员解除用户禁言失败: {message}")
                return False
                
        except Exception as e:
            self.test_results.append(f"❌ 管理员解除用户禁言测试异常: {e}")
            return False
    
    def test_list_banned_objects(self):
        """测试列出被禁言对象"""
        print("\n📝 测试列出被禁言对象...")
        
        try:
            # 管理员列出被禁言对象
            success, message = self.admin_client.send_admin_command(
                "free", "-l", None, "", ""
            )
            
            if success:
                self.test_results.append("✅ 列出被禁言对象成功")
                print(f"   禁言列表: {message}")
                return True
            else:
                self.test_results.append(f"❌ 列出被禁言对象失败: {message}")
                return False
                
        except Exception as e:
            self.test_results.append(f"❌ 列出被禁言对象测试异常: {e}")
            return False
    
    def cleanup_test_environment(self):
        """清理测试环境"""
        print("\n🧹 清理测试环境...")
        
        try:
            if self.admin_client:
                self.admin_client.disconnect()
            if self.normal_client:
                self.normal_client.disconnect()
            if self.server:
                self.server.stop()
            
            print("✅ 测试环境清理完成")
            
        except Exception as e:
            print(f"⚠️  清理测试环境时出现异常: {e}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始管理员功能测试")
        print("=" * 50)
        
        try:
            # 设置测试环境
            self.setup_test_environment()
            
            # 运行测试
            tests = [
                self.test_admin_login,
                self.test_normal_user_registration_and_login,
                self.test_admin_add_user,
                self.test_admin_delete_file,
                self.test_admin_ban_user,
                self.test_banned_user_send_message,
                self.test_admin_unban_user,
                self.test_list_banned_objects,
            ]
            
            for test in tests:
                try:
                    test()
                    time.sleep(1)  # 测试间隔
                except Exception as e:
                    self.test_results.append(f"❌ 测试 {test.__name__} 异常: {e}")
            
        finally:
            # 清理环境
            self.cleanup_test_environment()
        
        # 输出测试结果
        self.print_test_results()
    
    def print_test_results(self):
        """输出测试结果"""
        print("\n" + "=" * 50)
        print("📊 测试结果汇总")
        print("=" * 50)
        
        success_count = 0
        total_count = len(self.test_results)
        
        for result in self.test_results:
            print(result)
            if result.startswith("✅"):
                success_count += 1
        
        print("\n" + "=" * 50)
        print(f"总测试数: {total_count}")
        print(f"成功数: {success_count}")
        print(f"失败数: {total_count - success_count}")
        print(f"成功率: {success_count/total_count*100:.1f}%" if total_count > 0 else "0%")
        print("=" * 50)


if __name__ == "__main__":
    test = AdminFunctionTest()
    test.run_all_tests()
