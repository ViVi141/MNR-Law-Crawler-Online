# MNR Law Crawler - 数据流图表 (Mermaid版本)

> 如果您的Markdown查看器支持Mermaid图表，可以直接查看可视化流程图

## 系统整体架构

```mermaid
graph TB
    subgraph 前端层["前端层 (Vue 3 + TypeScript)"]
        A1[Policies.vue]
        A2[Tasks.vue]
        A3[Settings.vue]
        A4[Login.vue]
        A5[API Client<br/>axios]
        A1 --> A5
        A2 --> A5
        A3 --> A5
        A4 --> A5
    end
    
    subgraph API层["API 路由层 (FastAPI)"]
        B1[/api/auth]
        B2[/api/tasks]
        B3[/api/policies]
        B4[/api/config]
        B5[认证中间件<br/>JWT验证]
        B1 --> B5
        B2 --> B5
        B3 --> B5
        B4 --> B5
    end
    
    subgraph 服务层["业务服务层 (Services)"]
        C1[AuthService]
        C2[TaskService]
        C3[PolicyService]
        C4[ConfigService]
        C5[StorageService]
        C6[CacheService]
    end
    
    subgraph 核心层["核心爬虫层 (Core)"]
        D1[PolicyCrawler]
        D2[MNRSpider]
        D3[APIClient]
        D4[HTML Parsers]
        D5[Config]
        D1 --> D2
        D1 --> D3
        D2 --> D4
        D2 --> D5
    end
    
    subgraph 存储层["数据存储层"]
        E1[(PostgreSQL<br/>Database)]
        E2[本地文件系统]
        E3[S3对象存储<br/>可选]
    end
    
    subgraph 外部["外部数据源"]
        F1[政府信息公开平台<br/>gi.mnr.gov.cn]
        F2[政策法规库<br/>f.mnr.gov.cn]
    end
    
    A5 -->|HTTP/JSON| B1
    A5 -->|HTTP/JSON| B2
    A5 -->|HTTP/JSON| B3
    A5 -->|HTTP/JSON| B4
    
    B1 --> C1
    B2 --> C2
    B3 --> C3
    B4 --> C4
    
    C2 --> D1
    C3 --> C5
    C4 --> E1
    C5 --> C6
    C5 --> E2
    C5 --> E3
    
    D3 -->|HTTP请求| F1
    D3 -->|HTTP请求| F2
    
    C1 --> E1
    C2 --> E1
    C3 --> E1
    C2 --> E2
    C3 --> E2
```

## 任务创建与执行流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant F as 前端(Tasks.vue)
    participant A as API(tasks.py)
    participant TS as TaskService
    participant PC as PolicyCrawler
    participant MS as MNRSpider
    participant API_EXT as 外部API
    participant PS as PolicyService
    participant DB as 数据库
    participant FS as 文件系统
    
    U->>F: 创建爬取任务
    F->>A: POST /api/tasks
    A->>TS: create_task()
    TS->>DB: 创建任务记录(status: pending)
    
    alt autoStart=true
        TS->>TS: start_task() (后台线程)
        TS->>PC: 初始化PolicyCrawler
        PC->>MS: 创建MNRSpider
        
        loop 遍历数据源
            MS->>API_EXT: 请求政策列表
            API_EXT-->>MS: 返回HTML/JSON
            MS->>MS: 解析HTML
            MS->>MS: 时间过滤
            MS-->>PC: 返回Policy列表
        end
        
        loop 遍历Policy
            PC->>PS: save_policy()
            PS->>DB: 检查是否已存在(去重)
            alt 新政策
                PS->>DB: 保存政策记录
                PS->>FS: 保存JSON/Markdown/DOCX文件
                PS->>FS: (可选)上传S3
            end
            PS-->>PC: 返回保存结果
        end
        
        PC-->>TS: 返回统计信息
        TS->>DB: 更新任务状态和统计
        TS-->>A: 任务完成
    end
    
    A-->>F: 返回任务信息
    F-->>U: 显示任务状态
```

## 政策查询流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant F as 前端(Policies.vue)
    participant A as API(policies.py)
    participant PS as PolicyService
    participant DB as 数据库
    
    U->>F: 访问政策列表/搜索
    F->>A: GET /api/policies?page=1&keyword=...
    A->>A: 解析查询参数
    A->>PS: get_policies()
    PS->>DB: 构建SQL查询
    DB-->>PS: 返回政策列表和总数
    PS->>PS: 序列化为Schema
    PS-->>A: 返回政策数据
    A-->>F: 返回JSON响应
    F->>F: 渲染列表
    
    alt 用户点击详情
        U->>F: 点击政策
        F->>A: GET /api/policies/{id}
        A->>PS: get_policy_by_id()
        PS->>DB: 查询政策详情
        PS->>DB: 查询附件列表
        DB-->>PS: 返回完整信息
        PS-->>A: 返回政策详情
        A-->>F: 返回JSON响应
        F->>F: 渲染详情页
    end
```

## 用户认证流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant F as 前端(Login.vue)
    participant A as API(auth.py)
    participant AS as AuthService
    participant DB as 数据库
    participant Store as AuthStore
    
    U->>F: 输入用户名和密码
    F->>A: POST /api/auth/login
    A->>AS: verify_password()
    AS->>DB: 查询用户
    DB-->>AS: 返回用户记录
    AS->>AS: 验证密码哈希
    alt 验证成功
        AS->>AS: 生成JWT Token
        AS-->>A: 返回Token
        A-->>F: 返回Token和用户信息
        F->>Store: 保存Token
        Store->>F: 更新认证状态
        F->>F: 跳转到主页
    else 验证失败
        AS-->>A: 返回错误
        A-->>F: 返回401错误
        F-->>U: 显示错误消息
    end
```

## 配置管理流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant F as 前端(Settings.vue)
    participant A as API(config.py)
    participant CS as ConfigService
    participant DB as 数据库
    participant TS as TaskService
    
    U->>F: 修改爬取延迟配置
    F->>A: PUT /api/config/crawler
    A->>CS: update_crawler_config()
    CS->>DB: 保存配置到system_config表
    DB-->>CS: 保存成功
    CS-->>A: 返回更新后的配置
    A-->>F: 返回配置
    F-->>U: 显示保存成功
    
    Note over TS: 下次任务执行时
    TS->>CS: get_crawler_config()
    CS->>DB: 读取配置
    DB-->>CS: 返回配置
    CS-->>TS: 返回延迟值
    TS->>TS: 应用延迟配置到爬虫
```

## 文件下载流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant F as 前端
    participant A as API
    participant PS as PolicyService
    participant CS as CacheService
    participant S3 as S3Service
    participant FS as 文件系统
    
    U->>F: 点击下载按钮
    F->>A: GET /api/policies/{id}/file/{type}
    A->>PS: 获取文件路径
    PS->>CS: 检查本地缓存
    alt 缓存存在
        CS-->>PS: 返回缓存文件路径
        PS->>FS: 读取文件
        FS-->>PS: 返回文件流
        PS-->>A: 返回文件
        A-->>F: 返回Blob
        F->>F: 触发浏览器下载
    else 缓存不存在
        PS->>S3: 检查S3存储(如果启用)
        alt S3存在
            S3->>S3: 下载文件
            S3->>CS: 保存到本地缓存
            CS-->>PS: 返回文件路径
            PS->>FS: 读取文件
            FS-->>PS: 返回文件流
            PS-->>A: 返回文件
            A-->>F: 返回Blob
            F->>F: 触发浏览器下载
        else 文件不存在
            S3-->>PS: 返回404
            PS-->>A: 返回404错误
            A-->>F: 返回错误
            F-->>U: 显示错误消息
        end
    end
```

## 数据模型关系图

```mermaid
erDiagram
    User ||--o{ Task : creates
    Task ||--o{ TaskPolicy : has
    Policy ||--o{ TaskPolicy : belongs_to
    Policy ||--o{ Attachment : has
    User ||--o{ SystemConfig : manages
    
    User {
        int id PK
        string username
        string password_hash
        string email
    }
    
    Task {
        int id PK
        int user_id FK
        string task_name
        string task_type
        string status
        json config_json
        int policy_count
        int success_count
        int failed_count
    }
    
    Policy {
        int id PK
        string title
        string content
        date pub_date
        string source_name
        string category
        string publisher
    }
    
    Attachment {
        int id PK
        int policy_id FK
        string file_name
        string file_url
    }
    
    TaskPolicy {
        int task_id FK
        int policy_id FK
    }
    
    SystemConfig {
        string key PK
        string value
        string category
        boolean is_encrypted
    }
```

## 爬虫执行详细流程

```mermaid
flowchart TD
    Start([任务开始]) --> Init[初始化爬虫配置]
    Init --> LoadConfig[从数据库加载延迟配置]
    LoadConfig --> CheckDS{检查数据源}
    
    CheckDS -->|多数据源| MultiDS[按顺序处理每个数据源]
    CheckDS -->|单数据源| SingleDS[处理单个数据源]
    
    MultiDS --> LoopDS[遍历数据源列表]
    SingleDS --> CreateSpider[创建MNRSpider实例]
    LoopDS --> CreateSpider
    
    CreateSpider --> SelectParser{选择HTML解析器}
    SelectParser -->|gi.mnr.gov.cn| GIParser[GIMNRParser]
    SelectParser -->|f.mnr.gov.cn| FParser[FMNRParser]
    
    GIParser --> StartPage[开始翻页]
    FParser --> StartPage
    
    StartPage --> RequestAPI[请求API获取列表]
    RequestAPI --> ParseHTML[解析HTML响应]
    ParseHTML --> ExtractData[提取政策数据]
    ExtractData --> FilterDate{时间范围过滤}
    
    FilterDate -->|在范围内| CheckDup[去重检查]
    FilterDate -->|范围外| Skip[跳过]
    
    CheckDup -->|新政策| GetDetail[获取详情页]
    CheckDup -->|已存在| Skip
    
    GetDetail --> ParseDetail[解析详情内容]
    ParseDetail --> SaveDB[保存到数据库]
    
    SaveDB --> SaveFile[保存文件到存储]
    SaveFile --> UpdateStat[更新统计]
    
    UpdateStat --> CheckPage{是否还有下一页}
    CheckPage -->|是| NextPage[下一页]
    NextPage --> Delay[延迟0.5秒]
    Delay --> RequestAPI
    
    CheckPage -->|否| CheckDSNext{是否还有数据源}
    CheckDSNext -->|是| LoopDS
    CheckDSNext -->|否| SaveTask[保存任务结果]
    
    Skip --> UpdateStat
    
    SaveTask --> SendEmail{邮件通知启用?}
    SendEmail -->|是| Notify[发送邮件]
    SendEmail -->|否| Complete
    Notify --> Complete([任务完成])
```

## 配置加载流程

```mermaid
graph LR
    A[启动应用] --> B{配置来源}
    B -->|优先级1| C[数据库<br/>system_config表]
    B -->|优先级2| D[配置文件<br/>config.json]
    B -->|优先级3| E[默认值<br/>DEFAULT_CONFIG]
    
    C --> F[合并配置]
    D --> F
    E --> F
    
    F --> G[应用配置]
    G --> H[TaskService读取]
    H --> I[应用到爬虫]
```

## Docker 容器架构

```mermaid
graph TB
    subgraph Docker["Docker Compose 编排"]
        subgraph Frontend["前端容器 (Nginx 1.28)"]
            F1[Nginx 1.28<br/>Port: 3000]
            F2[静态文件<br/>/usr/share/nginx/html]
            F1 --> F2
        end
        
        subgraph Backend["后端容器 (FastAPI)"]
            B1[FastAPI<br/>Port: 8000]
            B2[Python 3.12<br/>uvicorn]
            B3[Entrypoint Script<br/>密钥生成]
            B3 --> B2
            B2 --> B1
        end
        
        subgraph Database["数据库容器 (PostgreSQL 18)"]
            D1[PostgreSQL 18<br/>Port: 5432]
            D2[Entrypoint Wrapper<br/>密码生成]
            D3[Save Password Script<br/>密码持久化]
            D2 --> D1
            D1 --> D3
        end
        
        subgraph Volumes["Docker Volumes"]
            V1[postgres_data<br/>数据库数据]
            V2[postgres_secrets<br/>密码共享卷]
            V3[crawled_data<br/>爬取文件]
            V4[cache_data<br/>缓存文件]
            V5[logs_data<br/>日志文件]
        end
        
        subgraph Networks["Docker Networks"]
            N1[frontend-network<br/>前端网络]
            N2[backend-network<br/>后端网络]
        end
    end
    
    F1 -->|HTTP代理| B1
    B1 -->|SQL连接| D1
    D1 --> V1
    D2 --> V2
    B3 -->|读取| V2
    B1 --> V3
    B1 --> V4
    B1 --> V5
    
    F1 -.-> N1
    B1 -.-> N2
    D1 -.-> N2
```

## Docker 自动配置流程

```mermaid
sequenceDiagram
    participant DC as Docker Compose
    participant DB as 数据库容器
    participant BE as 后端容器
    participant FE as 前端容器
    participant Vol as Docker Volumes
    
    DC->>DB: 启动数据库容器
    DB->>DB: docker-entrypoint-wrapper.sh
    alt 密码未设置或为默认值
        DB->>Vol: 检查持久化密码文件
        alt 文件存在
            Vol-->>DB: 返回已有密码
        else 文件不存在
            DB->>DB: 生成32字符随机密码
            DB->>Vol: 保存到持久化文件
        end
        DB->>Vol: 写入共享卷 /run/secrets/postgres_password
    end
    DB->>DB: PostgreSQL initdb
    DB->>DB: save-password.sh 保存密码
    DB-->>DC: 数据库就绪
    
    DC->>BE: 启动后端容器
    BE->>BE: docker-entrypoint.sh
    BE->>BE: 检查 JWT_SECRET_KEY
    alt JWT密钥未设置或为默认值
        BE->>Vol: 检查持久化密钥文件
        alt 文件存在
            Vol-->>BE: 返回已有密钥
        else 文件不存在
            BE->>BE: 生成128字符随机密钥
            BE->>Vol: 保存到持久化文件
        end
    end
    BE->>Vol: 从共享卷读取数据库密码
    Vol-->>BE: 返回密码
    BE->>BE: 更新 DATABASE_URL
    BE->>DB: 连接数据库
    DB-->>BE: 连接成功
    BE-->>DC: 后端就绪
    
    DC->>FE: 启动前端容器
    FE->>FE: Nginx 1.28 启动
    FE->>BE: 代理请求到后端
    BE-->>FE: 返回响应
    FE-->>DC: 前端就绪
```

---

*最后更新: 2025-12-09*

*这些图表展示了MNR Law Crawler系统的完整数据流和Docker容器架构。建议在支持Mermaid的Markdown查看器中查看以获得最佳可视化效果。*

