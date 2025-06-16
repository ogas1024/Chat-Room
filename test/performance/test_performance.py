"""
性能测试
测试系统在各种负载条件下的性能表现
"""

import pytest
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch

from server.database.models import DatabaseManager
from client.core.client import ChatClient
from test.utils.test_helpers import MockServer, MockClient


@pytest.mark.performance
class TestPerformance:
    """性能测试类"""
    
    def test_database_performance(self, db_manager):
        """测试数据库性能"""
        # 测试用户创建性能
        start_time = time.time()
        user_ids = []
        
        for i in range(100):
            user_id = db_manager.create_user(f"user_{i}", "password123")
            user_ids.append(user_id)
        
        create_time = time.time() - start_time
        
        # 验证性能指标
        assert create_time < 5.0, f"创建100个用户耗时过长: {create_time:.2f}s"
        assert len(user_ids) == 100
        
        # 测试用户查询性能
        start_time = time.time()
        
        for user_id in user_ids[:50]:  # 查询前50个用户
            user = db_manager.get_user_by_id(user_id)
            assert user is not None
        
        query_time = time.time() - start_time
        assert query_time < 1.0, f"查询50个用户耗时过长: {query_time:.2f}s"
    
    def test_concurrent_database_operations(self, db_manager):
        """测试并发数据库操作性能"""
        results = []
        errors = []
        
        def create_user_batch(start_id, count):
            """创建一批用户"""
            batch_results = []
            try:
                for i in range(count):
                    user_id = db_manager.create_user(f"batch_user_{start_id}_{i}", "password123")
                    batch_results.append(user_id)
            except Exception as e:
                errors.append(str(e))
            return batch_results
        
        start_time = time.time()
        
        # 使用线程池并发创建用户
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i in range(10):  # 10个线程，每个创建10个用户
                future = executor.submit(create_user_batch, i, 10)
                futures.append(future)
            
            for future in as_completed(futures):
                batch_results = future.result()
                results.extend(batch_results)
        
        total_time = time.time() - start_time
        
        # 验证结果
        assert len(errors) == 0, f"并发操作出现错误: {errors}"
        assert len(results) == 100, f"期望创建100个用户，实际创建{len(results)}个"
        assert total_time < 10.0, f"并发创建100个用户耗时过长: {total_time:.2f}s"
        
        # 计算平均每秒操作数
        ops_per_second = len(results) / total_time
        assert ops_per_second > 10, f"数据库操作性能过低: {ops_per_second:.2f} ops/s"
    
    def test_message_processing_performance(self, db_manager):
        """测试消息处理性能"""
        # 创建测试数据
        user_id = db_manager.create_user("test_user", "password123")
        group_id = db_manager.create_chat_group("test_group", False)
        
        # 测试消息保存性能
        start_time = time.time()
        message_ids = []
        
        for i in range(1000):
            message_id = db_manager.save_message(
                sender_id=user_id,
                chat_group_id=group_id,
                content=f"Test message {i}",
                message_type="chat"
            )
            message_ids.append(message_id)
        
        save_time = time.time() - start_time
        
        assert save_time < 10.0, f"保存1000条消息耗时过长: {save_time:.2f}s"
        assert len(message_ids) == 1000
        
        # 测试消息查询性能
        start_time = time.time()
        
        # 查询不同数量的历史消息
        for limit in [10, 50, 100, 500]:
            history = db_manager.get_chat_history(group_id, limit=limit)
            assert len(history) == min(limit, 1000)
        
        query_time = time.time() - start_time
        assert query_time < 2.0, f"查询消息历史耗时过长: {query_time:.2f}s"
    
    def test_concurrent_message_processing(self, db_manager):
        """测试并发消息处理性能"""
        # 创建测试数据
        user_ids = []
        for i in range(10):
            user_id = db_manager.create_user(f"msg_user_{i}", "password123")
            user_ids.append(user_id)
        
        group_id = db_manager.create_chat_group("perf_test_group", False)
        
        results = []
        
        def send_messages(user_id, message_count):
            """发送一批消息"""
            message_ids = []
            try:
                for i in range(message_count):
                    message_id = db_manager.save_message(
                        sender_id=user_id,
                        chat_group_id=group_id,
                        content=f"Message {i} from user {user_id}",
                        message_type="chat"
                    )
                    message_ids.append(message_id)
            except Exception as e:
                return {"error": str(e)}
            return {"success": len(message_ids)}
        
        start_time = time.time()
        
        # 10个用户并发发送消息
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for user_id in user_ids:
                future = executor.submit(send_messages, user_id, 50)  # 每个用户发送50条消息
                futures.append(future)
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        
        total_time = time.time() - start_time
        
        # 验证结果
        successful_results = [r for r in results if "success" in r]
        assert len(successful_results) == 10, "所有用户都应该成功发送消息"
        
        total_messages = sum(r["success"] for r in successful_results)
        assert total_messages == 500, f"期望发送500条消息，实际发送{total_messages}条"
        
        messages_per_second = total_messages / total_time
        assert messages_per_second > 50, f"消息处理性能过低: {messages_per_second:.2f} msg/s"
    
    def test_client_connection_performance(self):
        """测试客户端连接性能"""
        connection_times = []
        
        # 测试多次连接的性能
        for i in range(20):
            with patch('socket.socket') as mock_socket:
                mock_sock_instance = Mock()
                mock_socket.return_value = mock_sock_instance
                
                client = ChatClient("localhost", 8888)
                
                start_time = time.time()
                success = client.connect()
                connection_time = time.time() - start_time
                
                assert success is True
                connection_times.append(connection_time)
                
                client.disconnect()
        
        # 分析连接性能
        avg_connection_time = statistics.mean(connection_times)
        max_connection_time = max(connection_times)
        
        assert avg_connection_time < 0.1, f"平均连接时间过长: {avg_connection_time:.3f}s"
        assert max_connection_time < 0.5, f"最大连接时间过长: {max_connection_time:.3f}s"
    
    def test_message_serialization_performance(self):
        """测试消息序列化性能"""
        from shared.messages import ChatMessage
        
        # 创建测试消息
        messages = []
        for i in range(1000):
            message = ChatMessage(
                sender_id=1,
                sender_username="test_user",
                chat_group_id=1,
                chat_group_name="test_group",
                content=f"Test message {i} with some content to make it realistic"
            )
            messages.append(message)
        
        # 测试序列化性能
        start_time = time.time()
        
        serialized_messages = []
        for message in messages:
            json_str = message.to_json()
            serialized_messages.append(json_str)
        
        serialization_time = time.time() - start_time
        
        assert serialization_time < 1.0, f"序列化1000条消息耗时过长: {serialization_time:.3f}s"
        
        # 测试反序列化性能
        from shared.messages import parse_message
        
        start_time = time.time()
        
        parsed_messages = []
        for json_str in serialized_messages:
            parsed_message = parse_message(json_str)
            parsed_messages.append(parsed_message)
        
        deserialization_time = time.time() - start_time
        
        assert deserialization_time < 1.0, f"反序列化1000条消息耗时过长: {deserialization_time:.3f}s"
        assert len(parsed_messages) == 1000
    
    def test_memory_usage_under_load(self, db_manager):
        """测试负载下的内存使用"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 创建大量数据
        user_ids = []
        for i in range(500):
            user_id = db_manager.create_user(f"mem_user_{i}", "password123")
            user_ids.append(user_id)
        
        group_ids = []
        for i in range(50):
            group_id = db_manager.create_chat_group(f"mem_group_{i}", False)
            group_ids.append(group_id)
        
        # 创建大量消息
        for i in range(2000):
            user_id = user_ids[i % len(user_ids)]
            group_id = group_ids[i % len(group_ids)]
            db_manager.save_message(
                sender_id=user_id,
                chat_group_id=group_id,
                content=f"Memory test message {i}",
                message_type="chat"
            )
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # 验证内存使用合理
        assert memory_increase < 100, f"内存使用增长过多: {memory_increase:.2f}MB"
    
    def test_concurrent_client_simulation(self):
        """测试并发客户端模拟"""
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = Mock()
            mock_socket.return_value = mock_sock_instance
            
            results = []
            
            def simulate_client(client_id):
                """模拟客户端操作"""
                try:
                    client = ChatClient("localhost", 8888)
                    
                    # 连接
                    start_time = time.time()
                    success = client.connect()
                    if not success:
                        return {"client_id": client_id, "error": "connection_failed"}
                    
                    # 模拟一些操作
                    time.sleep(0.01)  # 模拟网络延迟
                    
                    client.disconnect()
                    
                    total_time = time.time() - start_time
                    return {"client_id": client_id, "time": total_time, "success": True}
                    
                except Exception as e:
                    return {"client_id": client_id, "error": str(e)}
            
            start_time = time.time()
            
            # 模拟50个并发客户端
            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = []
                for i in range(50):
                    future = executor.submit(simulate_client, i)
                    futures.append(future)
                
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
            
            total_time = time.time() - start_time
            
            # 分析结果
            successful_clients = [r for r in results if r.get("success")]
            failed_clients = [r for r in results if "error" in r]
            
            assert len(successful_clients) >= 45, f"成功客户端数量过少: {len(successful_clients)}/50"
            assert len(failed_clients) <= 5, f"失败客户端数量过多: {len(failed_clients)}"
            
            if successful_clients:
                avg_client_time = statistics.mean(r["time"] for r in successful_clients)
                assert avg_client_time < 0.5, f"平均客户端操作时间过长: {avg_client_time:.3f}s"
            
            clients_per_second = len(successful_clients) / total_time
            assert clients_per_second > 10, f"客户端处理性能过低: {clients_per_second:.2f} clients/s"
    
    def test_large_message_handling(self, db_manager):
        """测试大消息处理性能"""
        user_id = db_manager.create_user("large_msg_user", "password123")
        group_id = db_manager.create_chat_group("large_msg_group", False)
        
        # 测试不同大小的消息
        message_sizes = [100, 500, 1000, 2000]  # 字符数
        
        for size in message_sizes:
            large_content = "A" * size
            
            start_time = time.time()
            message_id = db_manager.save_message(
                sender_id=user_id,
                chat_group_id=group_id,
                content=large_content,
                message_type="chat"
            )
            save_time = time.time() - start_time
            
            assert message_id > 0
            assert save_time < 0.1, f"保存{size}字符消息耗时过长: {save_time:.3f}s"
            
            # 测试查询大消息
            start_time = time.time()
            history = db_manager.get_chat_history(group_id, limit=1)
            query_time = time.time() - start_time
            
            assert len(history) == 1
            assert len(history[0]['content']) == size
            assert query_time < 0.1, f"查询{size}字符消息耗时过长: {query_time:.3f}s"
