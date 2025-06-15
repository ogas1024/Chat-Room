### 界面 (Interface)

纯命令行界面实现，程序界面分为三大块：

* 聊天区  -- 左上角最大的一块 -- 显示聊天记录的区域。
* 输入区 -- 左下角稍小的一块  -- 用户输入区域。
* 状态区 -- 右侧一列-- 显示使用 `/list`命令的输出。
  * 当在一个聊天组中，默认显示当前聊天组用户列表 (需要包括用户的名称、用户的在线状态) (效果等效于 `/list -s`)。

三个区域之间应当需要分别刷新

TUI 使用 *Textual* 库 实现, 优先实现基本界面, 进阶的界面如果有时间继续完善

##### 聊天区

自己的消息需要使用特殊的颜色标明, 每条信息应该带有发送者昵称, 发送时间例如: 

```
Alice					<Sat May 24 23:12:36 CST 2025>
>hello Bob!🥰
```

格式类似于此, 非常需要优化

##### 输入区

普通的输入

##### 状态区

以比较优雅的方式输出列表

------

### 命令 (Commands)

进入系统是默认进入一个空的界面，但是输入框是可以输入的，然后可以在输入框中输入 `/{cmd}` 来执行各种操作，具体如下：

* `/?`
  
  * 列出所有可用的命令选项。
* `/help {options}`
  
  * 列出 `{option}` 命令的用法。例如 `/help send_files {文件路径}` : 将 `{文件路径}` 这个文件通过ftp发送。 (备注：FTP描述将更新为服务器中转)。
* `/login`
  
  * 进入登录状态，在状态列显示提示输入用户名/ID的提示，然后可以在输入框中输入用户名。用户名输入完毕后，状态列显示输入密码的提示，然后在输入框中输入密码。登录成功后在状态列打印登录成功，然后默认进入公频聊天。 (密码输入时应在界面上做掩码处理)。
* `/signin`
  
  * 进入注册状态。类似登录的流程走一遍注册的流程。 (密码输入时应在界面上做掩码处理)。
* `/info`
  
  * 在状态列显示当前的用户信息: 用户名(唯一)，ID(自动分配)，状态，已经加入的聊天组数量(私聊也算聊天组, 不过可以分开打印, 比如说总数x, 私聊y, 群聊x-y)，当前系统存在的聊天组总数，当前系统存在的用户总数，当前系统在线的用户总数。
* `/list {options}`
  * `-u` : 在状态列显示所有的用户 (需要包括用户的名称, ID, 用户的在线状态)。
  * `-s`: 在状态列显示**当前聊天组**的所有用户 (需要包括用户的名称, 用户的在线状态)。
  * `-c` : 在状态列显示所有**本用户已经加入的聊天组**。
  * `-g` : 在状态列显示所有的**用户列表长度>2**的聊天组 (也就是群聊而非私聊)。
* `/create_chat {chat_name} {users...}`
  
  * 创建一个聊天组, 该聊天组的 *别名* 是 `{chat_name}` , 初始成员为 `{users...}` (users为可变长参数)。将`users...` 加入到该聊天组的用户列表中。
* `/enter_chat {chat_name}`
  
  * 可以进入一个 *别名* 为 `{chat_name}` 的聊天组 **如果本用户存在于这个聊天组的用户列表中** (默认存在的公频的名称为: `public`)。
  * 加入聊天组之后自动加载该聊天组的聊天历史记录
* `/join_chat {chat_name}`
  
  * 加入到一个 *别名* 为 `{chat_name}` 的聊天组中, **将本用户加入到这个聊天组的用户列表中**。
* `/send_files {$file_path ... }` 
  这个命令应当具备以下的功能

  - 将用户 `$file_path(绝对路径)` 下的文件上传到服务器中, 这是一个可变长的参数, 意味着用户可以通过后面跟着多个文件的绝对路径, 一次上传多个文件

  - 上传的文件应当被存放在服务器的 `/项目根目录/server/$group_id/$文件名`下

    - 例如, 当前项目的根目录为`/home/ogas/Code/CN/Chat-Room` 

      用户在 `group_id==1` 的聊天组中发送了一个文件
      文件名为 `requirements.txt` 的文件将会被放在
      `/home/ogas/Code/CN/Chat-Room/server/1/requirement.txt`

    - 当然, 文件是要原封不动地存在对应的位置.
* `/recv_files {options}`

  * `-n {id}`: 接收该聊天组中文件id为 `{id}` 的文件。`id`是可变长参数, 用户可使用一条指令接收多个文件, 但是文件需要一个个下载
  * `-l`: 列出当前聊天记录中可供下载的文件。
    * 例如, 当用户在聊天组 `group_id==1` 中使用 `/recv_files -l` 就会在 `/home/ogas/Code/CN/Chat-Room/server/1/` 这个目录下遍历获取文件名记录在列表中, 先对列表中的文件名进行一个相应的格式化, 什么时候上传的, 文件大小, 文件的id, 原来的文件名是什么, 上传者是谁等必要的信息,  然后将这个文件名列表一次性输出出来.
* `/exit`
  
  * 退出系统, 将状态更新为离线。

------

### 功能细节 (Functional Details)

#### 1. 安全性 (Security)

* **数据传输**：除密码外，其他数据将以明文方式在客户端和服务器之间传输。
* **密码存储**：用户密码在注册时，服务器端将使用某种加密方式进行处理后存储在SQLite数据库中。登录验证时，对用户输入的密码进行同样的处理再进行比对。

#### 2. 数据库 (SQLite)

将使用 **SQLite** 数据库存储所有持久化数据，包括用户信息、聊天组信息、消息记录和文件元数据。数据库文件将部署在服务器端。

**初步表结构设想**:

* `users`
  * `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
  * `username` (TEXT, UNIQUE, NOT NULL)
  * `password_hash` (TEXT, NOT NULL)
  * `is_online` (INTEGER, DEFAULT 0) -- 0 for offline, 1 for online
* `chat_groups`
  * `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
  * `name` (TEXT, UNIQUE, NOT NULL) -- 聊天组别名
  * `is_private_chat` (INTEGER, DEFAULT 0) -- 1表示私聊 (成员数为2)，0表示群聊
  * `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
* `group_members`
  * `group_id` (INTEGER, FOREIGN KEY (`chat_groups.id`))
  * `user_id` (INTEGER, FOREIGN KEY (`users.id`))
  * PRIMARY KEY (`group_id`, `user_id`)
* `messages`
  * `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
  * `group_id` (INTEGER, FOREIGN KEY (`chat_groups.id`))
  * `sender_id` (INTEGER, FOREIGN KEY (`users.id`))
  * `content` (TEXT) -- 文本消息内容或文件传输的描述性信息
  * `message_type` (TEXT, DEFAULT 'text') -- 'text', 'file_notification', 'system_message'
  * `timestamp` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
* `files_metadata` (用于追踪文件信息)
  * `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
  * `original_filename` (TEXT, NOT NULL)
  * `server_filepath` (TEXT, NOT NULL, UNIQUE) -- 文件在服务器上的存储路径
  * `uploader_id` (INTEGER, FOREIGN KEY (`users.id`))
  * `chat_group_id` (INTEGER, FOREIGN KEY (`chat_groups.id`))
  * `upload_timestamp` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
  * `message_id` (INTEGER, FOREIGN KEY (`messages.id`), NULLABLE) -- 关联到通知此文件的消息

#### 3. 聊天记录 (Chat History)

* 全部聊天内容（文本消息和文件传输记录）将存储在服务器端的SQLite数据库中。
* 客户端登录时，可从服务器拉取其参与的聊天组的最新消息，实现漫游。
* 客户端本地可缓存一部分聊天记录，以提高显示速度和支持离线查看（可选功能）。

#### 4. 用户状态 (User Status)

* 用户登录聊天室即向服务器发送上线信息，服务器更新数据库中用户状态为在线。
* 用户退出程序 (`/exit`) 或连接意外断开，服务器将其状态更新为离线。
* 服务器端存储的用户状态发生改变时，应通知相关客户端（例如同一聊天组内的用户）更新其本地显示的用户状态。

#### 5. 聊天 (Chat)

* 一定要是**即时通信**, 也就是说在同一聊天组的一个人发送了信息, 该聊天组在线的用户一定要能即时看到这条信息, 离线的用户可以等上线了拉取聊天记录
* 所有聊天（包括私聊和群聊）均视为一个“聊天组”。私聊是成员数量为2的特殊聊天组。
* 默认存在一个名为 `public` 的公频聊天组，所有用户均可加入和发言。
* AI (glm-4-flash) 集成
  * AI 用户可作为系统内的一个特殊用户。
  * **私聊**：用户与AI私聊时，客户端将用户消息发送至服务器。服务器识别目标为AI后，将当前对话上下文作为prompt，通过API请求智谱服务。收到智谱的响应后，服务器将此响应作为AI的消息发送回给用户。
  * **群聊**：群聊消息中若包含 `@AI`，服务器将截取该消息作为prompt，并结合聊天组的上下文信息，请求智谱服务。AI的回复将作为一条新消息发送到该群聊中。

#### 6. 收发文件 (File Transfer - Server Mediated)

* 发送文件 (`/send_files {file_path...}`)
  1. 客户端用户输入命令，指定本地文件路径。
  2. 客户端将文件数据块通过socket连接发送给服务器。
  3. 服务器接收文件，将其存储在预定义的服务器文件存储区 (例如，按聊天组ID或日期分子文件夹)。
     1. 文件应该存储在 `server/$group_id/` 目录下, 文件名可以使用文件的`id`.
  4. 服务器在 `files_metadata` 表中记录文件元数据（原文件名、服务器路径、上传者、所属聊天组等）。
  5. 服务器在对应的聊天组的 `messages` 表中插入一条类型为 `file_notification` 的消息，内容可包含文件名、大小、上传者等信息，并关联到`files_metadata`的记录。
  6. 服务器将此文件通知消息广播给聊天组内所有在线成员。
* 接收文件 (`/recv_files`)
  1. `-n {file_id}`: 接收该聊天组中寻找与该聊天组 `group_id` 相同的文件, `id` 为 `{file_id}` 的文件
  2. `original_filename`是可变长参数, 用户可使用一条指令接收多个文件, 但是文件需要一个个下载
  3. `-l`: 列出当前聊天记录中可供下载的文件。
     * 例如, 当用户在聊天组 `group_id==1` 中使用 `/recv_files -l` 就会在 `/home/ogas/Code/CN/Chat-Room/server/1/` 这个目录下遍历获取文件名记录在列表中, 先对列表中的文件名进行一个相应的格式化, 什么时候上传的, 文件大小有多小等必要的信息,  然后将这个文件名列表一次性输出出来.
  4. 接收到的文件下载在 `client/Downloads/$username/` 目录下
  5. 收到的文件记得要重命名成原始的文件名 `original_filename` 而不是用于存储的文件 `id`
  6. 客户端向服务器发起文件下载请求，指明所需文件。
  7. 服务器根据请求，从其存储区读取文件数据，并通过socket连接将文件数据块发送给客户端。
  8. 客户端在界面提示用户文件接收成功及存储路径。

------

### 代码结构 (Code Structure)

使用最佳的模块化, 低耦合度的方式组织代码, 且不要滥用设计模式, **在模块化和复杂之间取得平衡**，将客户端和服务器端分离. 优先实现核心功能, TUI的优化优先级可以放在最后

**我不清楚这样是否是最佳的方式, 非常需要优化 **

